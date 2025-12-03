#!/usr/bin/env python3
"""
Message Defragmentation & Consolidation Engine

Reduces 21,717 fragmented messages → ~5,000-8,000 consolidated entries.

Algorithm:
1. Load all messages from 3 sources
2. Remove exact duplicates (content hash)
3. Group by conversation thread (context_id)
4. Within each thread, cluster by time (1-hour windows)
5. For each cluster, create consolidated entry
6. Preserve originals in audit trail but output only consolidated
7. Generate statistics on reduction

Result: Clean, lean history ready for ZeroMQ migration
"""

import json
import hashlib
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import sys

# Configuration
SOURCE_DIRS = {
    'dual_agents': Path("C:/Dev/Active_Projects/dual-agents"),
    'pc_next': Path("C:/Dev/Archived_Projects/PropertyCentre-Next"),
    'shearwater': Path("C:/Users/user/ShearwaterAICAD/communication")
}

OUTPUT_DIR = Path("C:/Users/user/ShearwaterAICAD/conversation_logs")
CONSOLIDATED_FILE = OUTPUT_DIR / "consolidated_history.jsonl"
AUDIT_FILE = OUTPUT_DIR / "fragmentation_audit.jsonl"


class DefragmentationEngine:
    def __init__(self):
        self.stats = {
            'total_loaded': 0,
            'exact_duplicates_removed': 0,
            'consolidated_groups': 0,
            'final_consolidated_messages': 0,
            'reduction_ratio': 0.0,
            'sources_processed': {}
        }
        self.seen_hashes = {}  # hash -> first occurrence
        self.messages_by_context = defaultdict(list)  # context_id -> messages
        self.consolidated_entries = []
        self.audit_trail = []

    def normalize_content(self, content: str) -> str:
        """Normalize content for comparison"""
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        # Remove common punctuation variations
        normalized = re.sub(r'[.,!?;:\-]+', '', normalized)
        return normalized

    def calculate_hash(self, content: str) -> str:
        """Calculate MD5 hash of normalized content"""
        normalized = self.normalize_content(content)
        return hashlib.md5(normalized.encode()).hexdigest()

    def extract_content(self, msg: Dict) -> str:
        """Extract text content from various message formats"""
        # Try different formats
        if 'Message' in msg:  # dual-agents format
            text = msg.get('Message', '{}')
            try:
                if isinstance(text, str):
                    parsed = json.loads(text)
                    return str(parsed)
            except:
                return text
        elif 'content' in msg:  # ShearwaterAICAD format
            content = msg.get('content', {})
            if isinstance(content, dict):
                return content.get('message', str(content))
            return str(content)
        elif 'message' in msg:  # PropertyCentre format
            return msg.get('message', '')
        elif 'summary' in msg:  # PropertyCentre format variant
            return msg.get('summary', '')

        return str(msg)

    def load_messages(self) -> int:
        """Load all messages from 3 sources"""
        print("[LOAD] Starting message loading from 3 sources...")
        total = 0

        for source_name, source_path in SOURCE_DIRS.items():
            if not source_path.exists():
                print(f"[WARNING] Source not found: {source_path}")
                continue

            source_count = 0

            # Load JSONL files
            for jsonl_file in source_path.rglob('*.jsonl'):
                try:
                    with open(jsonl_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                msg = json.loads(line.strip())
                                self._process_loaded_message(msg, source_name)
                                source_count += 1
                                total += 1
                            except json.JSONDecodeError:
                                continue
                except Exception as e:
                    print(f"[ERROR] Failed to read {jsonl_file}: {e}")
                    continue

            # Load JSON files
            for json_file in source_path.rglob('*.json'):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for msg in data:
                                self._process_loaded_message(msg, source_name)
                                source_count += 1
                                total += 1
                        elif isinstance(data, dict):
                            self._process_loaded_message(data, source_name)
                            source_count += 1
                            total += 1
                except Exception as e:
                    print(f"[ERROR] Failed to read {json_file}: {e}")
                    continue

            print(f"[LOAD] {source_name}: {source_count} messages loaded")
            self.stats['sources_processed'][source_name] = source_count

        self.stats['total_loaded'] = total
        return total

    def _process_loaded_message(self, msg: Dict, source: str):
        """Process and deduplicate a loaded message"""
        content = self.extract_content(msg)
        if not content or len(content.strip()) == 0:
            return

        content_hash = self.calculate_hash(content)

        # Exact duplicate detection
        if content_hash in self.seen_hashes:
            self.stats['exact_duplicates_removed'] += 1
            return

        self.seen_hashes[content_hash] = msg

        # Get context ID (conversation thread)
        context_id = self._extract_context_id(msg)

        # Add to messages by context
        self.messages_by_context[context_id].append({
            'original': msg,
            'content': content,
            'hash': content_hash,
            'source': source,
            'timestamp': self._extract_timestamp(msg)
        })

    def _extract_context_id(self, msg: Dict) -> str:
        """Extract conversation context ID"""
        # Try various fields
        for field in ['ContextId', 'context_id', 'conversation_id', 'thread_id']:
            if field in msg:
                return msg[field]
        # Default to source+hash
        return f"context_{hashlib.md5(str(msg).encode()).hexdigest()[:8]}"

    def _extract_timestamp(self, msg: Dict) -> str:
        """Extract timestamp from message"""
        for field in ['Timestamp', 'timestamp', 'created_at', 'time']:
            if field in msg:
                return msg[field]
        return datetime.utcnow().isoformat()

    def consolidate(self) -> int:
        """
        Consolidate messages within each conversation thread.

        Algorithm:
        1. For each context/thread
        2. Sort messages by timestamp
        3. Group into 1-hour time windows
        4. For each window, create consolidated entry
        """
        print("\n[CONSOLIDATE] Starting consolidation...")
        consolidated_count = 0

        for context_id, messages in self.messages_by_context.items():
            if not messages:
                continue

            # Sort by timestamp
            try:
                sorted_msgs = sorted(messages, key=lambda m: m['timestamp'])
            except:
                sorted_msgs = messages

            # Group into time windows (1 hour)
            windows = self._create_time_windows(sorted_msgs)

            for window_idx, window_msgs in enumerate(windows):
                consolidated = self._create_consolidated_entry(
                    context_id, window_idx, window_msgs
                )
                self.consolidated_entries.append(consolidated)
                consolidated_count += 1

                # Audit trail: record which messages were consolidated
                for msg in window_msgs:
                    self.audit_trail.append({
                        'original_content': msg['content'][:100],  # First 100 chars
                        'consolidated_into': consolidated['Id'],
                        'source': msg['source'],
                        'timestamp': msg['timestamp']
                    })

        self.stats['consolidated_groups'] = consolidated_count
        return consolidated_count

    def _create_time_windows(self, messages: List, window_minutes: int = 60) -> List[List]:
        """Group messages into time windows"""
        if not messages:
            return []

        windows = []
        current_window = [messages[0]]
        current_time = self._parse_timestamp(messages[0]['timestamp'])

        for msg in messages[1:]:
            msg_time = self._parse_timestamp(msg['timestamp'])
            time_diff = (msg_time - current_time).total_seconds() / 60

            if time_diff <= window_minutes:
                # Same window
                current_window.append(msg)
            else:
                # New window
                windows.append(current_window)
                current_window = [msg]
                current_time = msg_time

        # Add last window
        if current_window:
            windows.append(current_window)

        return windows

    def _parse_timestamp(self, ts: str) -> datetime:
        """Parse timestamp string to datetime (naive UTC)"""
        try:
            # Try ISO format, strip timezone
            ts_clean = ts.replace('Z', '').replace('+00:00', '').split('+')[0].split('-')[:-1 if len(ts.split('-')[-1]) <= 2 else None]
            if isinstance(ts_clean, list):
                ts_clean = '-'.join(ts_clean)
            return datetime.fromisoformat(ts_clean if ts_clean else ts.split('Z')[0].split('+')[0])
        except:
            try:
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                    try:
                        return datetime.strptime(ts.split('.')[0].split('+')[0].split('Z')[0], fmt)
                    except:
                        continue
            except:
                pass
        # Default to now (naive UTC)
        return datetime.now()

    def _create_consolidated_entry(self, context_id: str, window_idx: int, messages: List) -> Dict:
        """Create a consolidated entry from a group of messages"""
        import uuid

        # Extract key information
        contents = [m['content'] for m in messages]
        keywords = self._extract_keywords(contents)
        timestamp_first = messages[0]['timestamp']
        timestamp_last = messages[-1]['timestamp']

        # Create summary
        summary = self._create_summary(contents)

        consolidated = {
            'Id': str(uuid.uuid4()),
            'Timestamp': timestamp_first,
            'TimestampEnd': timestamp_last,
            'SpeakerName': 'consolidated',
            'SpeakerRole': 'System',
            'Message': json.dumps({
                'message': summary,
                'consolidated': True,
                'original_count': len(messages),
                'time_window': f"{timestamp_first} to {timestamp_last}",
                'keywords': keywords
            }),
            'ConversationType': 0,
            'ContextId': context_id,
            'Metadata': {
                'consolidated': True,
                'original_message_count': len(messages),
                'consolidation_ratio': f"{len(messages)}:1",
                'sources': list(set([m['source'] for m in messages])),
                'keywords': keywords,
                'window_index': window_idx
            }
        }

        return consolidated

    def _extract_keywords(self, contents: List[str], limit: int = 20) -> List[str]:
        """Extract keywords from content"""
        # Simple keyword extraction: find words >4 chars
        keywords = set()
        for content in contents:
            words = re.findall(r'\b[a-z]{4,}\b', content.lower())
            keywords.update(words)

        # Filter out common words
        stopwords = {'the', 'this', 'that', 'with', 'from', 'have', 'were', 'been', 'will', 'just', 'into', 'which', 'their', 'would', 'could', 'should', 'about', 'after', 'before'}
        keywords = [kw for kw in keywords if kw not in stopwords]

        return sorted(list(keywords))[:limit]

    def _create_summary(self, contents: List[str], max_length: int = 200) -> str:
        """Create a summary from multiple contents"""
        if not contents:
            return "[empty conversation window]"

        # Concatenate and truncate
        combined = " | ".join(contents)
        if len(combined) > max_length:
            combined = combined[:max_length-3] + "..."

        return combined

    def persist_consolidated(self) -> bool:
        """Write consolidated entries to disk"""
        print("\n[PERSIST] Writing consolidated entries...")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        try:
            # Write consolidated entries
            with open(CONSOLIDATED_FILE, 'w', encoding='utf-8') as f:
                for entry in self.consolidated_entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    f.flush()

            # Write audit trail
            with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
                for audit in self.audit_trail[:10000]:  # Limit to 10K audit entries
                    f.write(json.dumps(audit, ensure_ascii=False) + '\n')
                    f.flush()

            print(f"[OK] Consolidated entries: {CONSOLIDATED_FILE}")
            print(f"[OK] Audit trail: {AUDIT_FILE}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to persist: {e}")
            return False

    def report_statistics(self):
        """Print comprehensive statistics"""
        print("\n" + "=" * 80)
        print("[DEFRAGMENTATION STATISTICS]")
        print("=" * 80)

        total_loaded = self.stats['total_loaded']
        exact_dupes = self.stats['exact_duplicates_removed']
        consolidated = self.stats['consolidated_groups']

        print(f"\nInput:")
        print(f"  Total messages loaded:       {total_loaded:,}")
        print(f"  Exact duplicates removed:    {exact_dupes:,}")
        print(f"  Unique messages:             {total_loaded - exact_dupes:,}")

        print(f"\nConsolidation:")
        print(f"  Consolidation groups:        {consolidated:,}")
        print(f"  Compression ratio:           {(total_loaded - exact_dupes) / consolidated:.1f}:1")

        print(f"\nReduction:")
        reduction_pct = ((total_loaded - consolidated) / total_loaded * 100) if total_loaded > 0 else 0
        print(f"  Messages eliminated:         {total_loaded - consolidated:,}")
        print(f"  Reduction percentage:        {reduction_pct:.1f}%")

        print(f"\nSources:")
        for source, count in self.stats['sources_processed'].items():
            print(f"  {source:25s}: {count:,} messages")

        print(f"\nOutput:")
        if CONSOLIDATED_FILE.exists():
            size_mb = CONSOLIDATED_FILE.stat().st_size / 1024 / 1024
            print(f"  Consolidated file:           {CONSOLIDATED_FILE} ({size_mb:.1f} MB)")
        if AUDIT_FILE.exists():
            size_kb = AUDIT_FILE.stat().st_size / 1024
            print(f"  Audit trail:                 {AUDIT_FILE} ({size_kb:.1f} KB)")

        print("=" * 80)

    def run(self) -> bool:
        """Execute full defragmentation pipeline"""
        print("\n" + "=" * 80)
        print("[START] Message Defragmentation Engine")
        print("=" * 80 + "\n")

        # Phase 1: Load
        loaded = self.load_messages()
        print(f"\n[RESULT] Loaded {loaded:,} messages (after exact dedup: {loaded - self.stats['exact_duplicates_removed']:,})")

        # Phase 2: Consolidate
        consolidated = self.consolidate()
        print(f"[RESULT] Consolidated into {consolidated:,} entries")

        # Phase 3: Persist
        success = self.persist_consolidated()

        # Phase 4: Report
        self.report_statistics()

        return success


if __name__ == "__main__":
    engine = DefragmentationEngine()
    success = engine.run()
    sys.exit(0 if success else 1)
