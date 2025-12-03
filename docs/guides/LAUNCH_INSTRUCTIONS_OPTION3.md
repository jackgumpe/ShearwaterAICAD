# Launch Instructions: Option 3 - Full Parallel Execution
## Real-Time ZeroMQ + Block Consolidation + Phase 1 Development

**Date:** 2025-11-20
**Status:** Ready to launch
**Duration:** 5 minutes to get ZeroMQ live, then parallel work begins

---

## IMMEDIATE: Launch ZeroMQ System (5 minutes)

### Terminal A: Start Broker
```bash
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python zmq_broker_enhanced.py
```

**Wait for output:**
```
[*] Enhanced ZeroMQ Broker with Advanced Recording
[*] Listening for publishers on port 5555
[*] Listening for subscribers on port 5556
[*] Loaded 2,367 messages from previous session
[RECOVERY] System recovered with 2,367 clean messages
```

✅ Keep this terminal open and running. Do NOT close.

---

### Terminal B: Start Gemini Monitor (wait 2 seconds after A is ready)
```bash
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python gemini_monitor_loop_zmq.py
```

**Wait for output:**
```
[START] Gemini ZeroMQ Monitor Started
[*] Connected to broker at tcp://127.0.0.1:5556
[*] Subscribed to all topics
[READY] Waiting for messages...
```

✅ Keep this terminal open. This is Gemini's real-time listener.

---

### Terminal C: Start Claude Monitor (wait 2 seconds after B is ready)
```bash
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python claude_monitor_loop_zmq.py
```

**Wait for output:**
```
[START] Claude ZeroMQ Monitor Started
[*] Connected to broker at tcp://127.0.0.1:5556
[*] Subscribed to all topics
[READY] Waiting for messages...
```

✅ Keep this terminal open. This is Claude's real-time listener.

---

### Terminal D: Verify System is Live (in a new terminal)
```bash
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1

# Create test message
$msg = @{
    sender_id = "claude_code"
    message_id = "option3_launch_test"
    timestamp = Get-Date -AsUTC -Format "o"
    content = @{ message = "Option 3 launch: Real-time system + parallel development beginning" }
    metadata = @{
        ace_tier = "A"
        chain_type = "system_architecture"
        shl_tags = @("@Status-Ready", "@Decision-Made")
        sender_role = "Agent"
    }
} | ConvertTo-Json

$msg | Out-File "test_option3.json"
python send_message.py test_option3.json general
```

**Expected Results:**
- Broker (Terminal A): Shows `[LOG #1] claude_code on general | Tier:A | Chain:system_architecture`
- Gemini (Terminal B): Shows test message instantly
- Claude (Terminal C): Shows test message instantly
- **Latency: <50ms round-trip**

If all three show the message within 1 second: **✅ HANDSHAKE IS LIVE**

---

## PARALLEL TRACK 1: Keep File-Based Inbox (Optional)

**Terminal E: Keep old inbox running (or restart if needed)**
```bash
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python claude_monitor_loop.py
```

This allows you to keep using manual copy-paste as a backup while ZeroMQ gets tested.

---

## PARALLEL TRACK 2: Start Block Consolidation Development

### Phase 2a: Create block_consolidation_bot_v1.py

**Create:** `C:/Users/user/ShearwaterAICAD/block_consolidation_bot_v1.py`

This is your first bot that will:
- Load 2,367 messages from current_session.jsonl
- Generate embeddings using all-MiniLM-L6-v2
- Detect boundaries using semantic similarity (threshold 0.6) + time gaps (15 min)
- Create preliminary blocks
- Output to `conversation_logs/blocks_index_v1.jsonl`

**Skeleton to start with:**
```python
#!/usr/bin/env python3
"""
Block Consolidation Bot V1
Converts 2,367 messages into 300-400 conversation blocks using semantic segmentation.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import uuid

# Configuration
HISTORY_FILE = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/current_session.jsonl")
OUTPUT_FILE = Path("C:/Users/user/ShearwaterAICAD/conversation_logs/blocks_index_v1.jsonl")

# Algorithm parameters
SIMILARITY_THRESHOLD = 0.6
TIME_THRESHOLD = 900  # 15 minutes in seconds
MIN_BLOCK_SIZE = 5

def load_messages():
    """Load all messages from current_session.jsonl"""
    messages = []
    if not HISTORY_FILE.exists():
        print(f"[ERROR] {HISTORY_FILE} not found")
        return messages

    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                msg = json.loads(line.strip())
                messages.append(msg)
            except json.JSONDecodeError as e:
                print(f"[ERROR] Line {line_num}: {e}")

    print(f"[LOADED] {len(messages)} messages")
    return messages

def get_message_text(msg):
    """Extract text content from message"""
    if 'Message' in msg:
        content = msg['Message']
        if isinstance(content, str):
            try:
                content_dict = json.loads(content)
                return content_dict.get('message', str(content_dict))
            except:
                return content
        else:
            return str(content)
    return ""

def parse_timestamp(msg):
    """Parse timestamp from message"""
    timestamp_str = msg.get('Timestamp', '')
    try:
        # Handle various timestamp formats
        for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S']:
            try:
                return datetime.strptime(timestamp_str.replace('Z', ''), fmt)
            except:
                continue
        return datetime.now()
    except:
        return datetime.now()

def generate_embeddings(model, messages):
    """Generate embeddings for all messages"""
    print("[EMBEDDING] Generating embeddings for all messages...")
    texts = [get_message_text(msg) for msg in messages]
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"[EMBEDDING] Generated {len(embeddings)} embeddings")
    return embeddings

def detect_boundaries(messages, embeddings):
    """Detect conversation boundaries using semantic similarity + time"""
    print("[BOUNDARY_DETECTION] Analyzing message pairs...")
    boundaries = [0]  # Always start with first message

    for i in range(len(messages) - 1):
        msg_current = messages[i]
        msg_next = messages[i + 1]

        # Check time gap
        time_current = parse_timestamp(msg_current)
        time_next = parse_timestamp(msg_next)
        time_gap = (time_next - time_current).total_seconds()

        if time_gap > TIME_THRESHOLD:
            boundaries.append(i + 1)
            continue

        # Check semantic similarity
        similarity = cosine_similarity(
            [embeddings[i]],
            [embeddings[i + 1]]
        )[0][0]

        if similarity < SIMILARITY_THRESHOLD:
            boundaries.append(i + 1)

    boundaries.append(len(messages))  # Always end with last message
    print(f"[BOUNDARY_DETECTION] Found {len(boundaries) - 1} potential boundaries")
    return boundaries

def create_blocks(messages, boundaries):
    """Create blocks from boundaries"""
    print("[BLOCK_CREATION] Creating blocks...")
    blocks = []

    for i in range(len(boundaries) - 1):
        start_idx = boundaries[i]
        end_idx = boundaries[i + 1]

        # Skip tiny blocks
        if (end_idx - start_idx) < MIN_BLOCK_SIZE:
            continue

        block_messages = messages[start_idx:end_idx]

        # Extract metadata
        timestamp_start = parse_timestamp(block_messages[0])
        timestamp_end = parse_timestamp(block_messages[-1])
        duration_minutes = (timestamp_end - timestamp_start).total_seconds() / 60

        speakers = list(set(msg.get('Sender', 'Unknown') for msg in block_messages))

        block = {
            'block_id': f"block_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}",
            'timestamp_start': timestamp_start.isoformat() + 'Z',
            'timestamp_end': timestamp_end.isoformat() + 'Z',
            'duration_minutes': round(duration_minutes, 1),
            'message_count': len(block_messages),
            'speakers': speakers,
            'message_indices': list(range(start_idx, end_idx)),
            'confidence': 0.85,  # Placeholder
            'algorithm_version': '1.0'
        }

        blocks.append(block)

    print(f"[BLOCK_CREATION] Created {len(blocks)} blocks")
    return blocks

def save_blocks(blocks):
    """Save blocks to JSONL"""
    print(f"[SAVING] Writing {len(blocks)} blocks to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for block in blocks:
            f.write(json.dumps(block, ensure_ascii=False) + '\n')
    print(f"[SUCCESS] Blocks saved to {OUTPUT_FILE}")

def main():
    print("=" * 80)
    print("[START] Block Consolidation Bot V1")
    print("=" * 80)

    # Load model
    print("[MODEL] Loading sentence-transformers/all-MiniLM-L6-v2...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Load messages
    messages = load_messages()
    if not messages:
        print("[ERROR] No messages loaded")
        return False

    # Generate embeddings
    embeddings = generate_embeddings(model, messages)

    # Detect boundaries
    boundaries = detect_boundaries(messages, embeddings)

    # Create blocks
    blocks = create_blocks(messages, boundaries)

    # Save blocks
    save_blocks(blocks)

    print("=" * 80)
    print(f"[RESULT] Converted {len(messages)} messages to {len(blocks)} blocks")
    print(f"[RESULT] Average block size: {len(messages) // len(blocks)} messages")
    print("=" * 80)

    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
```

**To run:**
```bash
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python block_consolidation_bot_v1.py
```

Expected output: ~300-400 blocks from 2,367 messages

---

## PARALLEL TRACK 3: Phase 1 Component Development

While block consolidation runs in background, you can start Phase 1 component design:

### Components to build (from earlier docs):
1. **Recorder V2** - Enhanced message recording with clean 2,367-message history
2. **Bot Engine** - Consolidates messages (5-repeat threshold for E-Tier)
3. **Search Engine** - RAG queries on clean history (7-day window for C-Tier)
4. **BoatLog** - Test scenario for boat reconstruction workflow

These can be developed while block consolidation bot runs.

---

## EXECUTION TIMELINE

**T+0 minutes:** Launch Terminals A, B, C
**T+2 minutes:** Broker ready, Gemini connected
**T+4 minutes:** Claude connected
**T+5 minutes:** Verify with test message
**T+5 minutes:** Keep old inbox running in Terminal E (optional)
**T+5 minutes:** Create and run block_consolidation_bot_v1.py
**T+10 minutes:** Start Phase 1 component design while bot runs
**T+20 minutes:** block_consolidation_bot_v1.py completes, review blocks
**T+20-60 minutes:** Implement Phase 1 components + agent refinement
**T+60+ minutes:** Test everything together

---

## SUCCESS INDICATORS

✅ **ZeroMQ Live:**
- All three terminals show [READY]
- Test message delivered <50ms

✅ **Block Consolidation Started:**
- bot_v1.py running or completed
- blocks_index_v1.jsonl created with ~300-400 blocks

✅ **Parallel Development:**
- Phase 1 component designs in progress
- File-based inbox backup running

✅ **System Awareness:**
- All three terminals aware handshake is operational
- Ready to transition blocks to ZeroMQ when ready

---

## Notes

- **Inbox backup:** Keep old system running for 24-48 hours as fallback
- **Block consolidation:** V1 is intentionally simple (semantic + time only). V2 will add NER, dialogue acts, etc.
- **Testing:** Run bot_v1 on sample first (100 messages) before full 2,367
- **Feedback:** Use bot + agent feedback loop to improve daily

---

**Ready to launch? Run the three terminal commands above.**
