# Persistent Recording & Crash Recovery Guide

**Critical Requirement**: Every message must be recorded to disk immediately. If the broker or monitors crash, we can recover the complete conversation history.

---

## How It Works

### Original Broker vs. Persistent Broker

**zmq_broker.py** (Original):
- In-memory message deque (10,000 messages max)
- If broker crashes → messages lost
- Good for real-time, bad for recovery

**zmq_broker_persistent.py** (New):
- In-memory deque (10,000 messages)
- **PLUS** persistent JSONL log file on disk
- **PLUS** automatic session archiving
- **PLUS** recovery on startup
- If broker crashes → reload from disk on restart

### What Gets Recorded

Every message published to the broker is immediately written to disk:

```jsonl
{
  "message_num": 1,
  "topic": "test_topic",
  "sender": "claude_code",
  "timestamp": "2025-11-20T12:30:45.123Z",
  "tier": "A",
  "chain_type": "system_architecture",
  "shl_tags": ["@Status-Ready", "@A-Tier:Design-Review"],
  "message_id": "msg_001",
  "content": {
    "message": "Gemini, please review Phase 1 designs",
    "action": "design_review_request"
  }
}
```

---

## Directory Structure

```
ShearwaterAICAD/
├── zmq_broker_persistent.py         # New broker with recording
├── zmq_log_viewer.py                # Tool to view logs
└── conversation_logs/               # Auto-created by broker
    ├── current_session.jsonl        # Active conversation log
    └── archive/                     # Archived sessions
        ├── session_20251120_143022.jsonl
        ├── session_20251120_160045.jsonl
        └── ...
```

---

## Usage: Replace Old Broker with Persistent Broker

### Step 1: Update Terminal A (Broker Terminal)

Instead of:
```powershell
python zmq_broker.py
```

Use:
```powershell
python zmq_broker_persistent.py
```

**Expected Output:**
```
[*] ZeroMQ broker started with PERSISTENT RECORDING
[*] Listening for publishers on port 5555
[*] Listening for subscribers on port 5556
[*] Persisting all messages to: C:\Users\user\ShearwaterAICAD\conversation_logs\current_session.jsonl
[*] Storing last 10000 messages in memory.
[*] Loaded 0 messages from previous session
```

### Step 2: Everything Else Stays the Same

Terminals B (Gemini) and C (Claude) run unchanged:
```powershell
python gemini_monitor_loop_zmq.py
python claude_monitor_loop_zmq.py
```

The new broker is backward-compatible. All monitoring and messaging works identically.

---

## Recovery: If Broker Crashes

### Scenario: Broker crashes during active conversation

**Before (Old System)**:
- All in-memory messages lost
- Only recovery: check file inbox (slow, incomplete)

**After (Persistent System)**:
1. Restart the broker: `python zmq_broker_persistent.py`
2. On startup, broker loads all previous messages from disk
3. Output shows:
   ```
   [*] Loaded 247 messages from previous session
   [RECOVERY] System recovered with 247 messages from previous session
   ```
4. Messages automatically replayed to any reconnecting monitors
5. No data loss - full conversation history intact

**This is automatic.** Nothing you need to do except restart the broker.

---

## Viewing Recorded Conversations

### Command: View Recent Messages

```powershell
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python zmq_log_viewer.py --limit 20
```

**Output:**
```
[*] Loaded 247 messages from C:\Users\user\ShearwaterAICAD\conversation_logs\current_session.jsonl
[*] Showing 20 of 247 messages

[RECENT MESSAGES]:

================================================================================
[#228] claude_code → claude_design_request
[TIME] 2025-11-20T12:30:45.123Z
[TIER] A | [CHAIN] system_architecture
[ID] msg_001
[SHL] @Status-Ready, @A-Tier:Design-Review

[CONTENT]:
{
  "message": "Gemini, please review Phase 1 designs",
  "action": "design_review_request"
}
================================================================================
```

### Filter by Tier

Show only A-Tier (Architectural) messages:
```powershell
python zmq_log_viewer.py --tier A
```

### Filter by Domain Chain

Show only reconstruction chain messages:
```powershell
python zmq_log_viewer.py --chain reconstruction
```

### Filter by Sender

Show only Claude's messages:
```powershell
python zmq_log_viewer.py --sender claude_code
```

### Show Statistics

```powershell
python zmq_log_viewer.py --stats
```

**Output:**
```
[CONVERSATION STATISTICS]

[ACE Tier Distribution]
  A-Tier: 12 messages (5%)
  C-Tier: 48 messages (20%)
  E-Tier: 187 messages (75%)

[Domain Chains]
  photo_capture: 50 messages
  reconstruction: 75 messages
  quality_assessment: 45 messages
  system_architecture: 77 messages

[Senders]
  claude_code: 150 messages
  gemini_cli: 97 messages

[Time Range]
  From: 2025-11-20T12:30:45.123Z
  To:   2025-11-20T15:47:22.456Z
```

### View Archived Sessions

List all archived sessions:
```powershell
python zmq_log_viewer.py --list-archives
```

**Output:**
```
[*] Archived sessions in C:\Users\user\ShearwaterAICAD\conversation_logs\archive:
  1. session_20251120_143022.jsonl (156.2 KB) - 2025-11-20 14:30:22
  2. session_20251120_160045.jsonl (234.5 KB) - 2025-11-20 16:00:45
  3. session_20251120_180200.jsonl (89.3 KB) - 2025-11-20 18:02:00
```

### View Specific Archive

```powershell
python zmq_log_viewer.py --archive session_20251120_143022.jsonl --limit 50
```

---

## Automatic Session Archiving

### When Does Archiving Happen?

Sessions are archived when:
1. You manually stop the broker (Ctrl+C)
2. On daily rotation (can be configured)
3. When switching to new recording phase

### What Happens?

1. Current session (`current_session.jsonl`) is renamed with timestamp
2. Moved to `archive/` directory
3. New `current_session.jsonl` is created for new messages
4. Previous messages remain accessible via viewer

**Example**:
```
Before archive:
  conversation_logs/current_session.jsonl  (247 messages)

After archive:
  conversation_logs/archive/session_20251120_143022.jsonl  (247 messages)
  conversation_logs/current_session.jsonl  (empty, ready for new messages)
```

---

## Data Durability Guarantees

### What We're Protecting Against

1. **In-memory loss** (broker crash)
   - ✅ Prevented by disk persistence

2. **Partial writes** (power failure mid-write)
   - ✅ Prevented by `fsync()` (force OS to write to disk)

3. **Lost messages** (monitor disconnects)
   - ✅ Prevented by broker storing all messages

4. **Corrupted logs** (bad JSON)
   - ✅ Recovered by line-by-line parsing (skip bad lines)

### Technical Safeguards

```python
# Each message write:
f.write(json.dumps(log_entry) + '\n')  # Write entry
f.flush()                              # Flush buffer
os.fsync(f.fileno())                   # Force OS write
```

This ensures messages are permanently on disk within milliseconds.

---

## Log File Locations

**Current Session**:
```
C:\Users\user\ShearwaterAICAD\conversation_logs\current_session.jsonl
```

**All Archives**:
```
C:\Users\user\ShearwaterAICAD\conversation_logs\archive\
```

These are plain-text JSONL files, human-readable and searchable with any text editor.

---

## Backup Strategy

### Manual Backup

Backup your logs periodically:
```powershell
Copy-Item -Recurse "C:\Users\user\ShearwaterAICAD\conversation_logs" `
  -Destination "C:\Users\user\Backups\ShearwaterLogs_$(Get-Date -Format 'yyyyMMdd')"
```

### Automated Backup (Optional)

Create a scheduled task to backup logs daily:
```powershell
# In Windows Task Scheduler
# Trigger: Daily at 9 PM
# Action: Copy conversation_logs folder to external drive or cloud storage
```

---

## Summary

### Before (Vulnerable)
- File-based inbox (slow, inefficient)
- File monitoring with polling (10-30s latency)
- No persistent recording
- Crash = data loss

### After (Robust)
- ZeroMQ real-time messaging (<10ms latency)
- Automatic disk persistence
- Recovery on startup
- Full conversation history preserved
- Easy viewing and filtering

### Key Insight

**Recording happens automatically.** You don't need to do anything special. Just run `zmq_broker_persistent.py` instead of `zmq_broker.py`, and all messages are safely recorded to disk.

If the system crashes, restart the broker and all messages are recovered from disk.

---

## Next: Start with Persistent Broker

Use this startup sequence:

**Terminal A (Broker - CHANGED)**:
```powershell
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python zmq_broker_persistent.py  # CHANGED from zmq_broker.py
```

**Terminal B (Gemini - UNCHANGED)**:
```powershell
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python gemini_monitor_loop_zmq.py
```

**Terminal C (Claude - UNCHANGED)**:
```powershell
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1
python claude_monitor_loop_zmq.py
```

Everything else works identically. Persistence is transparent and automatic.
