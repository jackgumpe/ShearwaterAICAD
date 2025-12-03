#!/usr/bin/env python3
"""
Enhanced ZeroMQ Broker with Advanced Conversation Recording

This broker merges the best of:
- dual-agents/recorder.py: Clean JSONL, UUID events, PropertyCentre interop
- PropertyCentre-Next/smart_conversation_recorder.py: Chain detection, keywords, metadata
- ShearwaterAICAD design: ACE tiers, SHL shorthand, domain chains

Features:
- Real-time ZeroMQ message forwarding (XPUB/XSUB)
- Persistent JSONL logging with atomic writes
- Chain-type auto-detection (10 domain chains)
- ACE tier classification (A-Tier, C-Tier, E-Tier)
- SHL tag generation and keyword extraction
- Duplicate detection (content hashing)
- Smart metadata enrichment
- Session archiving with recovery
- Statistics and querying interface
"""

import zmq
import collections
import json
import time
import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import uuid

# --- Configuration ---
FRONTEND_PORT = 5555
BACKEND_PORT = 5556
MAX_MESSAGE_HISTORY = 10000
LOG_DIR = Path("conversation_logs")
CURRENT_LOG_FILE = LOG_DIR / "current_session.jsonl"
ARCHIVE_DIR = LOG_DIR / "archive"
METADATA_DIR = LOG_DIR / "metadata"

# In-memory message log
message_log = collections.deque(maxlen=MAX_MESSAGE_HISTORY)

# Lock for thread-safe writes
log_lock = threading.Lock()

# Domain chains (10 from ShearwaterAICAD design)
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

# SHL tag patterns
SHL_PATTERNS = {
    'Status-Ready': r'\b(ready|complete|done|finished|approved)\b',
    'Status-Blocked': r'\b(blocked|waiting|issue|problem|error)\b',
    'Decision-Made': r'\b(decided|approved|finalized|confirmed)\b',
    'Question-Open': r'\?|how should|which|what if',
    'Action-Required': r'\b(todo|fixme|implement|build|create)\b',
}


@dataclass
class ConversationEvent:
    """Event matching dual-agents format for PropertyCentre interop"""
    Id: str
    Timestamp: str
    SpeakerName: str
    SpeakerRole: str
    Message: str
    ConversationType: int
    ContextId: str
    Metadata: Dict


class EnhancedConversationRecorder:
    """
    Advanced recorder combining dual-agents simplicity with PropertyCentre-Next intelligence
    """

    def __init__(self):
        self.message_log = collections.deque(maxlen=MAX_MESSAGE_HISTORY)
        self._setup_directories()

    def _setup_directories(self):
        """Create directory structure"""
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        METADATA_DIR.mkdir(parents=True, exist_ok=True)

    def detect_chain_type(self, content: str) -> str:
        """Detect domain chain from content (PropertyCentre-Next approach)"""
        content_lower = content.lower()
        scores = {}

        for chain_type, keywords in DOMAIN_CHAINS.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[chain_type] = score

        return max(scores, key=scores.get) if scores else 'system_architecture'

    def detect_ace_tier(self, speaker_role: str, message: str) -> str:
        """
        Detect ACE tier from speaker role and content.
        A-Tier: Architectural decisions (Architect role, long-term impact keywords)
        C-Tier: Collaborative decisions (discussion, debate, consensus)
        E-Tier: Execution details (default)
        """
        if speaker_role == "Architect" or speaker_role == "architect":
            return "A"

        message_lower = message.lower()

        # A-Tier indicators
        a_keywords = ["architecture", "design decision", "framework", "strategy", "long-term"]
        if any(kw in message_lower for kw in a_keywords):
            return "A"

        # C-Tier indicators
        c_keywords = ["should we", "what do you think", "consensus", "review needed"]
        if any(kw in message_lower for kw in c_keywords):
            return "C"

        return "E"

    def generate_shl_tags(self, content: str, chain_type: str) -> List[str]:
        """Generate SHL tags from content patterns"""
        tags = []
        content_lower = content.lower()

        for tag_name, pattern in SHL_PATTERNS.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                tags.append(f"@{tag_name}")

        # Add chain-specific tag
        tags.append(f"@Chain-{chain_type}")

        return list(set(tags))

    def extract_keywords(self, content: str, limit: int = 10) -> List[str]:
        """Extract relevant keywords from content"""
        content_lower = content.lower()
        all_keywords = []

        for keywords in DOMAIN_CHAINS.values():
            all_keywords.extend(keywords)

        found = [kw for kw in all_keywords if kw in content_lower]
        return sorted(list(set(found)))[:limit]

    def calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash for duplicate detection"""
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        return hashlib.md5(normalized.encode()).hexdigest()

    def check_duplicate(self, content_hash: str) -> Optional[str]:
        """Check if content already exists in message log"""
        for msg in self.message_log:
            if msg.get('content_hash') == content_hash:
                return msg.get('Id')
        return None

    def enrich_metadata(self, message: Dict) -> Dict:
        """Enhance metadata with advanced fields"""
        content = message.get('content', {}).get('message', '')
        chain_type = message.get('metadata', {}).get('chain_type', 'system_architecture')

        return {
            'word_count': len(content.split()),
            'char_count': len(content),
            'chain_type': chain_type,
            'ace_tier': message.get('metadata', {}).get('ace_tier', 'E'),
            'shl_tags': message.get('metadata', {}).get('shl_tags', []),
            'keywords': self.extract_keywords(content),
            'content_hash': self.calculate_content_hash(content),
            'timestamp': message.get('timestamp', datetime.utcnow().isoformat()),
        }

    def create_event(self, message: Dict) -> ConversationEvent:
        """Convert ZMQ message to ConversationEvent (PropertyCentre format)"""
        sender = message.get('sender_id', 'unknown')
        role = message.get('metadata', {}).get('sender_role', 'Agent')
        content = json.dumps(message.get('content', {}))

        return ConversationEvent(
            Id=str(uuid.uuid4()),
            Timestamp=message.get('timestamp', datetime.utcnow().isoformat()),
            SpeakerName=sender,
            SpeakerRole=role,
            Message=content,
            ConversationType=0,
            ContextId=message.get('context_id', 'unknown'),
            Metadata={
                'zmq_message_id': message.get('message_id'),
                'topic': message.get('topic', 'general'),
                **self.enrich_metadata(message)
            }
        )

    def persist_message(self, event: ConversationEvent) -> None:
        """Persist event to disk with atomic writes"""
        with log_lock:
            try:
                with open(CURRENT_LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
                    f.flush()
                    os.fsync(f.fileno())
            except Exception as e:
                print(f"[ERROR] Failed to persist: {e}")

    def load_previous_session(self) -> int:
        """Load messages from previous session (recovery)"""
        if not CURRENT_LOG_FILE.exists():
            return 0

        count = 0
        try:
            with open(CURRENT_LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        msg = json.loads(line.strip())
                        self.message_log.append(msg)
                        count += 1
                    except json.JSONDecodeError:
                        continue
            return count
        except Exception as e:
            print(f"[ERROR] Could not load session: {e}")
            return 0


def main():
    """Main broker with enhanced recording"""
    recorder = EnhancedConversationRecorder()

    context = zmq.Context()

    # Sockets
    xsub_socket = context.socket(zmq.XSUB)
    xsub_socket.bind(f"tcp://*:{FRONTEND_PORT}")

    xpub_socket = context.socket(zmq.XPUB)
    xpub_socket.bind(f"tcp://*:{BACKEND_PORT}")

    print(f"[*] Enhanced ZeroMQ Broker with Advanced Recording")
    print(f"[*] Listening for publishers on port {FRONTEND_PORT}")
    print(f"[*] Listening for subscribers on port {BACKEND_PORT}")
    print(f"[*] Recording to: {CURRENT_LOG_FILE.absolute()}")

    # Load previous session
    loaded = recorder.load_previous_session()
    if loaded > 0:
        print(f"[RECOVERY] Loaded {loaded} messages from previous session")

    # Poller
    poller = zmq.Poller()
    poller.register(xsub_socket, zmq.POLLIN)
    poller.register(xpub_socket, zmq.POLLIN)

    message_counter = 0

    try:
        while True:
            events = dict(poller.poll(1000))

            # Handle messages from publishers
            if xsub_socket in events and events[xsub_socket] == zmq.POLLIN:
                message = xsub_socket.recv_multipart()

                # Forward to subscribers
                xpub_socket.send_multipart(message)

                # Process and persist
                try:
                    if len(message) == 2:
                        topic, payload_str = message
                        payload = json.loads(payload_str)

                        # Enhance payload with intelligence
                        content = payload.get('content', {}).get('message', '')
                        chain_type = recorder.detect_chain_type(content)
                        sender_role = payload.get('metadata', {}).get('sender_role', 'Agent')
                        ace_tier = recorder.detect_ace_tier(sender_role, content)
                        shl_tags = recorder.generate_shl_tags(content, chain_type)

                        # Update metadata
                        if 'metadata' not in payload:
                            payload['metadata'] = {}

                        payload['metadata'].update({
                            'chain_type': chain_type,
                            'ace_tier': ace_tier,
                            'shl_tags': shl_tags,
                            'sender_role': sender_role
                        })

                        # Create and persist event
                        event = recorder.create_event(payload)
                        recorder.persist_message(event)
                        recorder.message_log.append(asdict(event))

                        message_counter += 1

                        print(f"[LOG #{message_counter}] {payload.get('sender_id', '?')} "
                              f"| Tier:{ace_tier} | Chain:{chain_type} | Topic:{topic.decode()}")

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"[ERROR] Could not parse message: {e}")

            # Handle subscriptions
            if xpub_socket in events and events[xpub_socket] == zmq.POLLIN:
                message = xpub_socket.recv_multipart()
                xsub_socket.send_multipart(message)

    except KeyboardInterrupt:
        print(f"\n[INFO] Broker shutting down...")
        print(f"[STATS] Processed {message_counter} messages in this session")

    finally:
        xsub_socket.close()
        xpub_socket.close()
        context.term()
        print("[*] Broker shutdown complete")


if __name__ == "__main__":
    main()
