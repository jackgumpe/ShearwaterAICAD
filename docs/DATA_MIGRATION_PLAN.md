# Data Migration Plan: Unified Conversation Recording System

**Objective**: Merge existing dual-agents and PropertyCentre-Next recording systems into enhanced ZeroMQ broker with zero data loss and full feature preservation.

**Status**: Ready for smooth, thoughtful execution

---

## Executive Summary

### The Merge
We're integrating three proven systems:

1. **dual-agents/recorder.py** (Simplicity)
   - Clean JSONL append-only format
   - UUID-based event IDs
   - PropertyCentre-compatible field naming
   - Minimal, focused (108 lines)

2. **PropertyCentre-Next/smart_conversation_recorder.py** (Intelligence)
   - Chain-type auto-detection
   - Content hashing for duplicate detection
   - Keyword extraction
   - Advanced metadata enrichment
   - Statistics/querying interface

3. **ShearwaterAICAD design** (Modern requirements)
   - ZeroMQ Pub/Sub architecture
   - ACE tier classification (A/C/E)
   - SHL shorthand tags (@Status-*, @Chain-*, @Decision-*)
   - 10 domain chains (photo_capture, reconstruction, quality_assessment, etc.)
   - Real-time event-driven messaging

### Result: zmq_broker_enhanced.py
- Preserves all existing conversation data
- Adds advanced features (chain detection, duplicate detection, keywords)
- Enables real-time messaging with ZeroMQ
- Maintains backward compatibility with PropertyCentre format
- Provides recovery and statistics

---

## Phase 1: Inventory & Assessment

### 1.1 Data Inventory

**Question**: Where is existing conversation data stored?

Run these commands to inventory:

```bash
# Find all JSONL files from dual-agents
find C:/Dev/Active_Projects/dual-agents -name "*.jsonl" -type f

# Find all files from PropertyCentre-Next
find C:/Dev/Archived_Projects/PropertyCentre-Next -name "*.jsonl" -o -name "*.json" -type f

# Check ShearwaterAICAD for existing messages
dir C:/Users/user/ShearwaterAICAD/communication/ /s
ls C:/Users/user/ShearwaterAICAD/conversation_logs/ -R
```

### 1.2 Data Volume Assessment

For each source, determine:
- Total message count
- Size in MB
- Time span (earliest to latest timestamp)
- Message types represented

**Expected Output Format**:
```
=== dual-agents Inventory ===
Files: 5 JSONL files
Total Messages: 12,450
Total Size: 85 MB
Time Range: 2024-01-15 to 2025-11-20
Key Chains: reconstruction (45%), photo_capture (30%), system_architecture (25%)

=== PropertyCentre-Next Inventory ===
Files: 8 JSON/JSONL files
Total Messages: 8,920
Total Size: 62 MB
Time Range: 2023-06-01 to 2025-10-31
Key Chains: data_management (40%), ui_ux (35%), testing_validation (25%)

=== ShearwaterAICAD (Current) ===
Files: 1 JSON file
Total Messages: 347
Total Size: 2.1 MB
Time Range: 2025-11-19 to 2025-11-20
```

---

## Phase 2: Schema Mapping & Transformation

### 2.1 Dual-Agents Format

**Source Format** (recorder.py):
```python
@dataclass
class ConversationEvent:
    Id: str                    # UUID
    Timestamp: str            # ISO 8601
    SpeakerName: str          # "claude_code"
    SpeakerRole: str          # "Agent" | "Architect"
    Message: str              # JSON string of content
    ConversationType: int     # 0 = default
    ContextId: str            # conversation ID
    Metadata: Dict            # Custom metadata
```

**Transformation to Enhanced Format**:
```python
# Add these fields to existing dual-agents records:
{
    # Original dual-agents fields (preserved)
    "Id": "abc123...",
    "Timestamp": "2025-11-20T12:30:45.123Z",
    "SpeakerName": "claude_code",
    "SpeakerRole": "Agent",
    "Message": "{...}",
    "ConversationType": 0,
    "ContextId": "context_001",
    "Metadata": {...},

    # NEW: Added by enhanced recorder
    "chain_type": "system_architecture",    # Auto-detected
    "ace_tier": "A",                        # Auto-detected from role + content
    "shl_tags": ["@Status-Ready", "@A-Tier:Design-Review"],  # Auto-generated
    "keywords": ["architecture", "design", "framework"],       # Auto-extracted
    "content_hash": "a1b2c3d4e5f6...",     # MD5 for dedup
    "zmq_metadata": {
        "topic": "general",
        "message_id": "msg_001",
        "broker_received": "2025-11-20T12:30:45.456Z"
    }
}
```

**Mapping Logic**:
```python
def transform_dual_agents_event(original_event: Dict) -> Dict:
    """Transform dual-agents event to enhanced format"""
    content = json.loads(original_event.get('Message', '{}'))
    content_str = original_event.get('Message', '')

    enhanced = {
        # Preserve all original fields
        **original_event,

        # Add detected fields
        'chain_type': detect_chain_type(content_str),
        'ace_tier': detect_ace_tier(original_event.get('SpeakerRole', 'Agent'), content_str),
        'shl_tags': generate_shl_tags(content_str),
        'keywords': extract_keywords(content_str),
        'content_hash': calculate_content_hash(content_str),

        # Add ZMQ metadata
        'zmq_metadata': {
            'source_system': 'dual-agents',
            'migrated_at': datetime.utcnow().isoformat(),
            'migration_version': '1.0'
        }
    }

    return enhanced
```

### 2.2 PropertyCentre-Next Format

**Source Format** (smart_conversation_recorder.py):
```python
{
    "timestamp": "2025-10-31T14:22:15.123Z",
    "chain_type": "data_management",
    "summary": "Database optimization discussion",
    "keywords": ["database", "performance", "indexing"],
    "content_hash": "f6e5d4c3b2a1...",
    "filepath": "conversations/data_management/...",
    "source_url": "https://...",
    "extraction_method": "manual",
    "word_count": 450,
    "char_count": 2800
}
```

**Transformation to Enhanced Format**:
```python
def transform_propertycenter_event(pc_event: Dict) -> Dict:
    """Transform PropertyCentre-Next event to enhanced format"""

    # Reconstruct message from available data
    if 'full_content' in pc_event:
        message_content = pc_event['full_content']
    else:
        message_content = pc_event.get('summary', '')

    enhanced = {
        # Core fields (reconstruct from PropertyCentre data)
        'Id': str(uuid.uuid4()),  # Generate new UUID
        'Timestamp': pc_event.get('timestamp', datetime.utcnow().isoformat()),
        'SpeakerName': pc_event.get('speaker_name', 'unknown'),
        'SpeakerRole': pc_event.get('speaker_role', 'Agent'),
        'Message': json.dumps({
            'message': message_content,
            'source': 'PropertyCentre-Next'
        }),
        'ConversationType': 0,
        'ContextId': pc_event.get('context_id', 'unknown'),

        # Preserve PropertyCentre metadata
        'Metadata': {
            'original_filepath': pc_event.get('filepath'),
            'source_url': pc_event.get('source_url'),
            'extraction_method': pc_event.get('extraction_method'),
            'word_count': pc_event.get('word_count'),
            'char_count': pc_event.get('char_count'),
            'pc_next_version': pc_event.get('version', 'unknown')
        },

        # PropertyCentre-Next intelligence (already computed)
        'chain_type': pc_event.get('chain_type', 'system_architecture'),
        'keywords': pc_event.get('keywords', []),
        'content_hash': pc_event.get('content_hash'),

        # Add enhanced fields
        'ace_tier': detect_ace_tier_from_content(message_content),
        'shl_tags': generate_shl_tags(message_content),

        # Add ZMQ metadata
        'zmq_metadata': {
            'source_system': 'PropertyCentre-Next',
            'migrated_at': datetime.utcnow().isoformat(),
            'migration_version': '1.0'
        }
    }

    return enhanced
```

### 2.3 ShearwaterAICAD (Current) Format

**Source Format** (current file-based inbox):
```python
{
    "sender_id": "claude_code",
    "message_id": "test_001",
    "timestamp": "2025-11-20T12:30:45.123Z",
    "content": {
        "message": "Hello Gemini!",
        "action": "test_message"
    },
    "metadata": {
        "ace_tier": "E",
        "chain_type": "system_architecture",
        "shl_tags": ["@Status-Ready", "@Test-Message"]
    }
}
```

**Transformation to Enhanced Format**:
```python
def transform_shearwater_event(sw_event: Dict) -> Dict:
    """Transform ShearwaterAICAD event to enhanced format"""

    message_content = sw_event.get('content', {}).get('message', '')
    metadata = sw_event.get('metadata', {})

    enhanced = {
        # Map to PropertyCentre format
        'Id': str(uuid.uuid4()),  # or preserve existing if present
        'Timestamp': sw_event.get('timestamp', datetime.utcnow().isoformat()),
        'SpeakerName': sw_event.get('sender_id', 'unknown'),
        'SpeakerRole': metadata.get('sender_role', 'Agent'),
        'Message': json.dumps(sw_event.get('content', {})),
        'ConversationType': 0,
        'ContextId': sw_event.get('context_id', 'unknown'),
        'Metadata': metadata,

        # Preserve ShearwaterAICAD data
        'chain_type': metadata.get('chain_type', 'system_architecture'),
        'ace_tier': metadata.get('ace_tier', 'E'),
        'shl_tags': metadata.get('shl_tags', []),
        'keywords': metadata.get('keywords', []),
        'content_hash': metadata.get('content_hash'),

        # Add ZMQ metadata
        'zmq_metadata': {
            'source_system': 'ShearwaterAICAD',
            'message_id': sw_event.get('message_id'),
            'migrated_at': datetime.utcnow().isoformat(),
            'migration_version': '1.0'
        }
    }

    return enhanced
```

---

## Phase 3: Migration Strategy

### 3.1 Pre-Migration Validation

**BEFORE** touching any data:

```bash
# 1. Create backup of all source data
mkdir C:/Users/user/Backups/ShearwaterAICAD_Migration_$(date +%Y%m%d_%H%M%S)

# 2. Copy all source JSONL/JSON files
cp C:/Dev/Active_Projects/dual-agents/**/*.jsonl backup/
cp C:/Dev/Archived_Projects/PropertyCentre-Next/**/*.json* backup/
cp C:/Users/user/ShearwaterAICAD/communication/ backup/

# 3. Verify backup integrity
ls -lhR backup/
find backup/ -name "*.jsonl" -o -name "*.json" | wc -l
```

**Validation Checklist**:
- [ ] Backup created and verified
- [ ] All source files readable
- [ ] Total size recorded
- [ ] Checksums computed (sha256sum)

### 3.2 Migration Script

**Create `migrate_to_zmq_broker.py`**:

```python
#!/usr/bin/env python3
"""
Migration script: Convert dual-agents, PropertyCentre-Next, and current ShearwaterAICAD
messages to enhanced ZeroMQ broker format.
"""

import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

# Configuration
BACKUP_DIR = Path("C:/Users/user/Backups/ShearwaterAICAD_Migration_PRE")
SOURCE_DIRS = {
    'dual_agents': Path("C:/Dev/Active_Projects/dual-agents"),
    'pc_next': Path("C:/Dev/Archived_Projects/PropertyCentre-Next"),
    'shearwater': Path("C:/Users/user/ShearwaterAICAD/communication")
}
OUTPUT_FILE = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/migrated_history.jsonl")

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

class MigrationEngine:
    def __init__(self):
        self.stats = {
            'total_migrated': 0,
            'dual_agents_count': 0,
            'pc_next_count': 0,
            'shearwater_count': 0,
            'errors': 0,
            'duplicates_skipped': 0
        }
        self.seen_hashes = set()
        self.output_file = OUTPUT_FILE
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def detect_chain_type(self, content: str) -> str:
        """Detect domain chain from content"""
        content_lower = content.lower()
        scores = {}

        for chain_type, keywords in DOMAIN_CHAINS.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[chain_type] = score

        return max(scores, key=scores.get) if scores else 'system_architecture'

    def detect_ace_tier(self, speaker_role: str, message: str) -> str:
        """Detect ACE tier"""
        if speaker_role.lower() in ['architect', 'architecture']:
            return 'A'

        message_lower = message.lower()
        a_keywords = ["architecture", "design decision", "framework", "strategy", "long-term"]
        if any(kw in message_lower for kw in a_keywords):
            return 'A'

        c_keywords = ["should we", "what do you think", "consensus", "review needed"]
        if any(kw in message_lower for kw in c_keywords):
            return 'C'

        return 'E'

    def generate_shl_tags(self, content: str, chain_type: str) -> List[str]:
        """Generate SHL tags"""
        tags = []
        content_lower = content.lower()

        for tag_name, pattern in SHL_PATTERNS.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                tags.append(f"@{tag_name}")

        tags.append(f"@Chain-{chain_type}")
        return list(set(tags))

    def calculate_content_hash(self, content: str) -> str:
        """Calculate MD5 hash"""
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        return hashlib.md5(normalized.encode()).hexdigest()

    def transform_dual_agents(self, event: Dict) -> Optional[Dict]:
        """Transform dual-agents event"""
        try:
            message_str = event.get('Message', '{}')
            if isinstance(message_str, str):
                try:
                    content = json.loads(message_str)
                except:
                    content = {'message': message_str}
            else:
                content = message_str

            # Check for duplicate
            content_hash = self.calculate_content_hash(message_str)
            if content_hash in self.seen_hashes:
                self.stats['duplicates_skipped'] += 1
                return None
            self.seen_hashes.add(content_hash)

            enhanced = {
                **event,
                'chain_type': self.detect_chain_type(message_str),
                'ace_tier': self.detect_ace_tier(event.get('SpeakerRole', 'Agent'), message_str),
                'shl_tags': self.generate_shl_tags(message_str, self.detect_chain_type(message_str)),
                'keywords': self._extract_keywords(message_str),
                'content_hash': content_hash,
                'zmq_metadata': {
                    'source_system': 'dual-agents',
                    'migrated_at': datetime.utcnow().isoformat(),
                    'migration_version': '1.0'
                }
            }
            return enhanced
        except Exception as e:
            print(f"[ERROR] Failed to transform dual-agents event: {e}")
            self.stats['errors'] += 1
            return None

    def transform_pc_next(self, event: Dict) -> Optional[Dict]:
        """Transform PropertyCentre-Next event"""
        try:
            message_content = event.get('summary', event.get('content', ''))

            # Check for duplicate
            content_hash = self.calculate_content_hash(message_content)
            if content_hash in self.seen_hashes:
                self.stats['duplicates_skipped'] += 1
                return None
            self.seen_hashes.add(content_hash)

            enhanced = {
                'Id': str(uuid.uuid4()),
                'Timestamp': event.get('timestamp', datetime.utcnow().isoformat()),
                'SpeakerName': event.get('speaker_name', 'unknown'),
                'SpeakerRole': event.get('speaker_role', 'Agent'),
                'Message': json.dumps({'message': message_content, 'source': 'PropertyCentre-Next'}),
                'ConversationType': 0,
                'ContextId': event.get('context_id', 'unknown'),
                'Metadata': event,
                'chain_type': event.get('chain_type', self.detect_chain_type(message_content)),
                'ace_tier': self.detect_ace_tier(event.get('speaker_role', 'Agent'), message_content),
                'shl_tags': self.generate_shl_tags(message_content, event.get('chain_type', 'system_architecture')),
                'keywords': event.get('keywords', self._extract_keywords(message_content)),
                'content_hash': content_hash,
                'zmq_metadata': {
                    'source_system': 'PropertyCentre-Next',
                    'migrated_at': datetime.utcnow().isoformat(),
                    'migration_version': '1.0'
                }
            }
            return enhanced
        except Exception as e:
            print(f"[ERROR] Failed to transform PropertyCentre-Next event: {e}")
            self.stats['errors'] += 1
            return None

    def transform_shearwater(self, event: Dict) -> Optional[Dict]:
        """Transform ShearwaterAICAD event"""
        try:
            content = event.get('content', {})
            message_str = content.get('message', '') if isinstance(content, dict) else str(content)

            # Check for duplicate
            content_hash = self.calculate_content_hash(message_str)
            if content_hash in self.seen_hashes:
                self.stats['duplicates_skipped'] += 1
                return None
            self.seen_hashes.add(content_hash)

            metadata = event.get('metadata', {})
            enhanced = {
                'Id': str(uuid.uuid4()),
                'Timestamp': event.get('timestamp', datetime.utcnow().isoformat()),
                'SpeakerName': event.get('sender_id', 'unknown'),
                'SpeakerRole': metadata.get('sender_role', 'Agent'),
                'Message': json.dumps(content),
                'ConversationType': 0,
                'ContextId': event.get('context_id', 'unknown'),
                'Metadata': metadata,
                'chain_type': metadata.get('chain_type', self.detect_chain_type(message_str)),
                'ace_tier': metadata.get('ace_tier', self.detect_ace_tier(metadata.get('sender_role', 'Agent'), message_str)),
                'shl_tags': metadata.get('shl_tags', self.generate_shl_tags(message_str, metadata.get('chain_type', 'system_architecture'))),
                'keywords': metadata.get('keywords', self._extract_keywords(message_str)),
                'content_hash': content_hash,
                'zmq_metadata': {
                    'source_system': 'ShearwaterAICAD',
                    'message_id': event.get('message_id'),
                    'migrated_at': datetime.utcnow().isoformat(),
                    'migration_version': '1.0'
                }
            }
            return enhanced
        except Exception as e:
            print(f"[ERROR] Failed to transform ShearwaterAICAD event: {e}")
            self.stats['errors'] += 1
            return None

    def _extract_keywords(self, content: str, limit: int = 10) -> List[str]:
        """Extract keywords"""
        all_keywords = []
        for keywords in DOMAIN_CHAINS.values():
            all_keywords.extend(keywords)

        found = [kw for kw in all_keywords if kw in content.lower()]
        return sorted(list(set(found)))[:limit]

    def persist_event(self, event: Dict) -> bool:
        """Write event to JSONL"""
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
                f.flush()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to persist event: {e}")
            return False

    def migrate_source(self, source_name: str, source_path: Path, transform_func) -> int:
        """Migrate all files from a source"""
        print(f"\n[MIGRATE] Starting {source_name} migration...")
        count = 0

        if not source_path.exists():
            print(f"[WARNING] Source path not found: {source_path}")
            return 0

        # Find all JSONL and JSON files
        for file_path in source_path.rglob('*.jsonl'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            event = json.loads(line.strip())
                            transformed = transform_func(event)
                            if transformed:
                                if self.persist_event(transformed):
                                    count += 1
                        except json.JSONDecodeError as e:
                            print(f"[WARNING] {source_name}: Line {line_num} invalid JSON: {e}")
                            continue
            except Exception as e:
                print(f"[ERROR] Failed to read {file_path}: {e}")
                continue

        # Also check for JSON files
        for file_path in source_path.rglob('*.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for event in data:
                            transformed = transform_func(event)
                            if transformed:
                                if self.persist_event(transformed):
                                    count += 1
                    elif isinstance(data, dict):
                        transformed = transform_func(data)
                        if transformed:
                            if self.persist_event(transformed):
                                count += 1
            except Exception as e:
                print(f"[ERROR] Failed to read {file_path}: {e}")
                continue

        print(f"[OK] {source_name}: Migrated {count} events")
        return count

    def run(self) -> bool:
        """Execute full migration"""
        print("=" * 80)
        print("[START] ShearwaterAICAD Data Migration")
        print("=" * 80)
        print(f"[OUTPUT] {self.output_file}")

        # Migrate from each source
        self.stats['dual_agents_count'] = self.migrate_source(
            'dual-agents',
            SOURCE_DIRS['dual_agents'],
            self.transform_dual_agents
        )

        self.stats['pc_next_count'] = self.migrate_source(
            'PropertyCentre-Next',
            SOURCE_DIRS['pc_next'],
            self.transform_pc_next
        )

        self.stats['shearwater_count'] = self.migrate_source(
            'ShearwaterAICAD',
            SOURCE_DIRS['shearwater'],
            self.transform_shearwater
        )

        self.stats['total_migrated'] = (
            self.stats['dual_agents_count'] +
            self.stats['pc_next_count'] +
            self.stats['shearwater_count']
        )

        # Print results
        print("\n" + "=" * 80)
        print("[RESULTS] Migration Complete")
        print("=" * 80)
        print(f"dual-agents:        {self.stats['dual_agents_count']:,} events")
        print(f"PropertyCentre-Next: {self.stats['pc_next_count']:,} events")
        print(f"ShearwaterAICAD:     {self.stats['shearwater_count']:,} events")
        print(f"TOTAL MIGRATED:      {self.stats['total_migrated']:,} events")
        print(f"DUPLICATES SKIPPED:  {self.stats['duplicates_skipped']:,}")
        print(f"ERRORS:              {self.stats['errors']:,}")
        print(f"OUTPUT FILE:         {self.output_file} ({self.output_file.stat().st_size / 1024 / 1024:.1f} MB)")
        print("=" * 80)

        return self.stats['errors'] == 0

if __name__ == "__main__":
    engine = MigrationEngine()
    success = engine.run()
    exit(0 if success else 1)
```

### 3.3 Migration Steps

**Step 1: Backup All Source Data**
```bash
mkdir -p "C:/Users/user/Backups/ShearwaterAICAD_Migration_$(date +%Y%m%d_%H%M%S)"
cp -r "C:/Dev/Active_Projects/dual-agents" backup/
cp -r "C:/Dev/Archived_Projects/PropertyCentre-Next" backup/
cp -r "C:/Users/user/ShearwaterAICAD/communication" backup/
```

**Step 2: Create Migration Script**
Save the script above as `migrate_to_zmq_broker.py` in ShearwaterAICAD directory

**Step 3: Run Migration**
```bash
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python migrate_to_zmq_broker.py
```

**Step 4: Verify Output**
```bash
# Check migrated data
wc -l conversation_logs/migrated_history.jsonl
head -5 conversation_logs/migrated_history.jsonl  # Inspect first few records
tail -5 conversation_logs/migrated_history.jsonl  # Inspect last few records
```

---

## Phase 4: Validation & Quality Assurance

### 4.1 Data Integrity Checks

**Create `validate_migration.py`**:

```python
#!/usr/bin/env python3
"""Validate migrated data integrity and quality"""

import json
from pathlib import Path
from collections import defaultdict

def validate_migration():
    output_file = Path("conversation_logs/migrated_history.jsonl")

    if not output_file.exists():
        print("[ERROR] Migrated file not found")
        return False

    stats = {
        'total_records': 0,
        'valid_records': 0,
        'missing_fields': defaultdict(int),
        'chain_types': defaultdict(int),
        'ace_tiers': defaultdict(int),
        'sources': defaultdict(int),
        'errors': []
    }

    print("[VALIDATE] Starting migration validation...")

    with open(output_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            stats['total_records'] += 1

            try:
                record = json.loads(line.strip())

                # Check required fields
                required = ['Id', 'Timestamp', 'SpeakerName', 'Message', 'chain_type', 'ace_tier']
                for field in required:
                    if field not in record:
                        stats['missing_fields'][field] += 1
                    else:
                        stats['valid_records'] += 1

                # Count chain types
                stats['chain_types'][record.get('chain_type', 'unknown')] += 1

                # Count ACE tiers
                stats['ace_tiers'][record.get('ace_tier', 'E')] += 1

                # Count sources
                source = record.get('zmq_metadata', {}).get('source_system', 'unknown')
                stats['sources'][source] += 1

            except json.JSONDecodeError as e:
                stats['errors'].append(f"Line {line_num}: {e}")

    # Print results
    print("\n" + "=" * 80)
    print("[VALIDATION RESULTS]")
    print("=" * 80)
    print(f"Total Records:           {stats['total_records']:,}")
    print(f"Valid Records:           {stats['valid_records']:,}")

    if stats['missing_fields']:
        print("\n[MISSING FIELDS]")
        for field, count in stats['missing_fields'].items():
            print(f"  {field}: {count} records")

    print("\n[CHAIN TYPE DISTRIBUTION]")
    for chain, count in sorted(stats['chain_types'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / stats['total_records'] * 100) if stats['total_records'] > 0 else 0
        print(f"  {chain}: {count:,} ({pct:.1f}%)")

    print("\n[ACE TIER DISTRIBUTION]")
    for tier in ['A', 'C', 'E']:
        count = stats['ace_tiers'].get(tier, 0)
        pct = (count / stats['total_records'] * 100) if stats['total_records'] > 0 else 0
        print(f"  {tier}-Tier: {count:,} ({pct:.1f}%)")

    print("\n[SOURCE DISTRIBUTION]")
    for source, count in sorted(stats['sources'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / stats['total_records'] * 100) if stats['total_records'] > 0 else 0
        print(f"  {source}: {count:,} ({pct:.1f}%)")

    if stats['errors']:
        print(f"\n[ERRORS] {len(stats['errors'])} errors during validation")
        for error in stats['errors'][:10]:  # Show first 10
            print(f"  {error}")

    print("=" * 80)
    success = len(stats['errors']) == 0 and stats['valid_records'] == stats['total_records']
    print(f"[RESULT] {'PASSED' if success else 'FAILED'}")
    return success

if __name__ == "__main__":
    success = validate_migration()
    exit(0 if success else 1)
```

**Run Validation**:
```bash
python validate_migration.py
```

### 4.2 Comparison Checks

**Verify data consistency**:

```bash
# Count records in each source
echo "=== Source Record Counts ==="
echo "dual-agents:"
find C:/Dev/Active_Projects/dual-agents -name "*.jsonl" -exec wc -l {} \; | awk '{s+=$1} END {print s}'

echo "PropertyCentre-Next:"
find C:/Dev/Archived_Projects/PropertyCentre-Next -name "*.json*" -exec wc -l {} \; | awk '{s+=$1} END {print s}'

echo "ShearwaterAICAD:"
find C:/Users/user/ShearwaterAICAD/communication -name "*.json" -exec wc -l {} \; | awk '{s+=$1} END {print s}'

echo "Migrated total:"
wc -l C:/Users/user/ShearwaterAICAD/conversation_logs/migrated_history.jsonl
```

---

## Phase 5: Switchover & Activation

### 5.1 Pre-Switchover Checklist

- [ ] Backup created and verified (Phase 3.1)
- [ ] Migration script ready (Phase 3.2)
- [ ] Migration completed successfully (Phase 3.3)
- [ ] Validation passed (Phase 4.1)
- [ ] zmq_broker_enhanced.py tested in standalone mode
- [ ] Old system (claude_monitor_loop.py) gracefully shut down
- [ ] New ZMQ monitors ready to start

### 5.2 Switchover Procedure

**Step 1: Stop Old System**
```bash
# Kill old file-based monitors
# (These will be naturally replaced by ZMQ monitors)
```

**Step 2: Load Migrated Data into Broker**
```bash
# The zmq_broker_enhanced.py will load migrated_history.jsonl on startup
# and make all messages available to new subscribers
```

**Step 3: Start New ZMQ System**

**Terminal A (Broker)**:
```bash
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python zmq_broker_enhanced.py
```

**Terminal B (Gemini Monitor)**:
```bash
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python gemini_monitor_loop_zmq.py
```

**Terminal C (Claude Monitor)**:
```bash
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python claude_monitor_loop_zmq.py
```

### 5.3 Post-Switchover Verification

**Check Broker Status**:
```bash
# Broker should show:
# [*] Loaded XXXXX messages from previous session
# [RECOVERY] System recovered with XXXXX messages

# Test that data is available via log viewer:
python zmq_log_viewer.py --stats
```

**Sample Output**:
```
[*] Loaded 21,717 messages from C:\Users\user\ShearwaterAICAD\conversation_logs\migrated_history.jsonl

[CONVERSATION STATISTICS]

[ACE Tier Distribution]:
  A-Tier: 1,234 messages (5.7%)
  C-Tier: 4,321 messages (19.9%)
  E-Tier: 16,162 messages (74.4%)

[Domain Chains]:
  photo_capture: 5,432 messages
  reconstruction: 6,789 messages
  quality_assessment: 3,210 messages
  ...

[Senders]:
  claude_code: 12,450 messages
  gemini_cli: 8,920 messages
  unknown: 347 messages
```

---

## Phase 6: Rollback Plan (If Needed)

### If Migration Fails

1. **Stop new ZMQ system** (Ctrl+C in all terminals)
2. **Restore from backup**:
   ```bash
   cp -r backup/dual-agents/* C:/Dev/Active_Projects/dual-agents/
   cp -r backup/PropertyCentre-Next/* C:/Dev/Archived_Projects/PropertyCentre-Next/
   cp -r backup/communication/* C:/Users/user/ShearwaterAICAD/communication/
   ```
3. **Restart old system**:
   ```bash
   python claude_monitor_loop.py  # or gemini_monitor_loop.py
   ```
4. **Investigate** what went wrong and retry migration

### If Switchover Fails

1. **Kill new ZMQ processes**
2. **Restore conversation_logs from backup**:
   ```bash
   rm -rf C:/Users/user/ShearwaterAICAD/conversation_logs
   cp -r backup/conversation_logs C:/Users/user/ShearwaterAICAD/
   ```
3. **Restart old monitors** to resume
4. **Diagnose** and fix ZMQ broker issues before retrying

---

## Summary: Safe, Thoughtful Migration

### What We're Doing
- **Preserving** all existing data from 3 systems
- **Enhancing** with chain detection, duplicate detection, SHL tags
- **Integrating** into single unified ZeroMQ-based system
- **Validating** data integrity at every step
- **Backing up** everything before touching anything
- **Providing** rollback if anything goes wrong

### Timeline
- Phase 1 (Inventory): 15 minutes
- Phase 2 (Schema Mapping): Already complete (mapped above)
- Phase 3 (Migration): 30-60 minutes depending on data volume
- Phase 4 (Validation): 10-15 minutes
- Phase 5 (Switchover): 5 minutes
- **Total: ~90 minutes**

### Success Criteria
✅ All messages from 3 systems merged into single JSONL
✅ Zero data loss (duplicate detection prevents re-ingestion)
✅ Chain types auto-detected for all messages
✅ ACE tiers classified for all messages
✅ SHL tags generated for all messages
✅ Old system data fully preserved in backup
✅ New ZMQ system live and operational
✅ Full conversation history queryable via zmq_log_viewer.py

---

**Next Step**: Run the inventory phase to determine exact data volumes, then proceed with confidence.
