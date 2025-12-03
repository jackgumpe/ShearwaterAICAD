#!/usr/bin/env python3
"""
Migrate CLEAN, defragmented history to ZeroMQ broker format.

This script reads the already-consolidated consolidated_history.jsonl
and enriches it with ACE tier, chain type, SHL tags, keywords.

Much faster than migrate_to_zmq_broker.py since data is already deduplicated.
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import uuid
import sys

# Configuration
CLEAN_HISTORY = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/consolidated_history.jsonl")
OUTPUT_FILE = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/zmq_ready_history.jsonl")

# Domain chains for auto-detection
DOMAIN_CHAINS = {
    'photo_capture': ['photo', 'image', 'camera', 'capture', 'upload', 'scan'],
    'reconstruction': ['nerf', 'gaussian', 'mesh', '3d model', 'reconstruction', 'training'],
    'quality_assessment': ['quality', 'f1 score', 'artifacts', 'accuracy', 'validation'],
    'unity_integration': ['unity', 'gameobject', 'import', 'export', 'lod', 'material'],
    'token_optimization': ['token', 'cost', 'optimization', 'efficiency', 'budget'],
    'system_architecture': ['architecture', 'design', 'framework', 'pattern', 'strategy'],
    'agent_collaboration': ['agent', 'collaboration', 'coordination', 'handshake', 'sync'],
    'data_management': ['database', 'storage', 'persistence', 'cache', 'index'],
    'ui_ux': ['ui', 'ux', 'interface', 'user', 'display', 'interaction'],
    'testing_validation': ['test', 'validation', 'qa', 'benchmark', 'metrics']
}

SHL_PATTERNS = {
    'Status-Ready': r'\b(ready|complete|done|finished|approved)\b',
    'Status-Blocked': r'\b(blocked|waiting|issue|problem|error)\b',
    'Decision-Made': r'\b(decided|approved|finalized|confirmed)\b',
    'Question-Open': r'\?|how should|which|what if',
    'Action-Required': r'\b(todo|fixme|implement|build|create)\b',
}


def detect_chain_type(content: str) -> str:
    """Detect domain chain from content"""
    content_lower = content.lower()
    scores = {}

    for chain_type, keywords in DOMAIN_CHAINS.items():
        score = sum(1 for kw in keywords if kw in content_lower)
        if score > 0:
            scores[chain_type] = score

    return max(scores, key=scores.get) if scores else 'system_architecture'


def detect_ace_tier(speaker_role: str, message: str) -> str:
    """Detect ACE tier"""
    if speaker_role and 'architect' in speaker_role.lower():
        return 'A'

    message_lower = message.lower()
    a_keywords = ["architecture", "design decision", "framework", "strategy", "long-term"]
    if any(kw in message_lower for kw in a_keywords):
        return 'A'

    c_keywords = ["should we", "what do you think", "consensus", "review needed"]
    if any(kw in message_lower for kw in c_keywords):
        return 'C'

    return 'E'


def generate_shl_tags(content: str, chain_type: str) -> List[str]:
    """Generate SHL tags"""
    tags = []
    content_lower = content.lower()

    for tag_name, pattern in SHL_PATTERNS.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            tags.append(f"@{tag_name}")

    tags.append(f"@Chain-{chain_type}")
    return list(set(tags))


def extract_keywords(content: str, limit: int = 10) -> List[str]:
    """Extract keywords"""
    all_keywords = []
    for keywords in DOMAIN_CHAINS.values():
        all_keywords.extend(keywords)

    found = [kw for kw in all_keywords if kw in content.lower()]
    return sorted(list(set(found)))[:limit]


def process_clean_message(msg: Dict) -> Dict:
    """Enrich a message from consolidated history"""
    content = msg.get('Message', '{}')
    if isinstance(content, str):
        try:
            content_dict = json.loads(content)
            content_text = content_dict.get('message', str(content_dict))
        except:
            content_text = content
    else:
        content_text = str(content)

    speaker_role = msg.get('SpeakerRole', 'Agent')
    chain_type = detect_chain_type(content_text)
    ace_tier = detect_ace_tier(speaker_role, content_text)
    shl_tags = generate_shl_tags(content_text, chain_type)
    keywords = extract_keywords(content_text)

    # Add enriched fields
    msg['chain_type'] = chain_type
    msg['ace_tier'] = ace_tier
    msg['shl_tags'] = shl_tags
    msg['keywords'] = keywords
    msg['zmq_ready'] = True

    return msg


def main():
    """Enrich clean history for ZeroMQ broker"""
    if not CLEAN_HISTORY.exists():
        print(f"[ERROR] Clean history not found: {CLEAN_HISTORY}")
        return False

    print("=" * 80)
    print("[START] Enriching Clean History for ZeroMQ")
    print("=" * 80)
    print(f"[INPUT]  {CLEAN_HISTORY}")
    print(f"[OUTPUT] {OUTPUT_FILE}\n")

    count = 0
    errors = 0

    with open(CLEAN_HISTORY, 'r', encoding='utf-8') as in_f:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_f:
            for line_num, line in enumerate(in_f, 1):
                try:
                    msg = json.loads(line.strip())
                    enriched = process_clean_message(msg)
                    out_f.write(json.dumps(enriched, ensure_ascii=False) + '\n')
                    out_f.flush()
                    count += 1

                    if count % 500 == 0:
                        print(f"[PROGRESS] Processed {count} messages...")

                except json.JSONDecodeError as e:
                    print(f"[ERROR] Line {line_num}: {e}")
                    errors += 1
                except Exception as e:
                    print(f"[ERROR] Line {line_num}: {e}")
                    errors += 1

    print(f"\n[RESULT] Processed {count} clean messages")
    print(f"[RESULT] Errors: {errors}")

    if OUTPUT_FILE.exists():
        size_mb = OUTPUT_FILE.stat().st_size / 1024 / 1024
        print(f"[RESULT] Output file: {size_mb:.1f} MB")

    print("=" * 80)
    print("[SUCCESS] Ready for ZeroMQ broker")
    print("=" * 80)

    return errors == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
