# Real-Time Autonomous Communication Deployment Guide

**Status**: Ready to Deploy
**Date**: 2025-11-20
**Objective**: Enable true real-time back-and-forth conversation between Claude Code and Gemini CLI

---

## What This Enables

Once deployed, the system will:
- **Gemini**: Automatically detect new tasks in `gemini_cli_inbox/` every 30 seconds
- **Claude**: Automatically detect new responses in `claude_code_inbox/` every 10 seconds
- **Notifications**: Clear console messages when new tasks arrive
- **Real-time conversation**: Agents respond to each other within 30-90 seconds (no manual relay needed)

This creates a "texting-like" experience where both agents continuously monitor for new messages.

---

## Current Message State

### Messages Waiting for Gemini (in gemini_cli_inbox/)
```
✓ PHASE_1_COMPONENT_SPECS_PENDING.json - Phase 1 component specifications
✓ PHASE_1_TASK_ASSIGNMENT_PENDING.json - Phase 1 task assignment
✓ AUTONOMOUS_INBOX_PROTOCOL_PENDING.json - Autonomous monitoring protocol
✓ 002_ARCHITECTURE_DECISIONS_PENDING.json - Architecture Q1-Q4 decisions
✓ 001_HANDSHAKE_INIT_PENDING.json - Initial handshake
+ 4 test messages (TEST_001/002/003 and basic echo tests)
```

**Total pending**: 10 messages

### Messages Waiting for Claude (in claude_code_inbox/)
```
✓ phase_1_launch_RESULT.json - Gemini accepts Phase 1 supervisor role
✓ autonomous_protocol_RESULT.json - Gemini accepts autonomous protocol
✓ test_001_RESULT.json - Test response 1
✓ test_002_RESULT.json - Test response 2
✓ test_003_RESULT.json - Test response 3
```

**Total ready**: 5 messages

---

## Deployment Steps

### Step 1: Verify Directory Structure

All communication directories should exist:

```
C:/Users/user/ShearwaterAICAD/communication/
├── claude_code_inbox/       (WHERE Claude receives from Gemini)
├── claude_code_outbox/      (WHERE Claude sends to Gemini)
├── claude_code_archive/     (WHERE Claude's processed messages go)
├── gemini_cli_inbox/        (WHERE Gemini receives from Claude)
├── gemini_cli_outbox/       (WHERE Gemini sends to Claude)
└── gemini_cli_archive/      (WHERE Gemini's processed messages go)
```

Status: ✓ All directories confirmed existing

### Step 2: Monitor Scripts Ready

Two Python scripts are ready to deploy:

**A) `C:/Users/user/ShearwaterAICAD/claude_monitor_loop.py`**
- Monitors Claude's inbox every 10 seconds
- Looks for `*_RESULT.json` files from Gemini
- Processes responses automatically
- Can run in a separate terminal or background

**B) `C:/Users/user/ShearwaterAICAD/gemini_monitor_loop.py`**
- Monitors Gemini's inbox every 30 seconds
- Looks for `*_PENDING.json` files from Claude
- Notifies Gemini when tasks arrive
- Prints full message content for Gemini to read
- Should run in Gemini's terminal environment

### Step 3: Start Claude's Monitor

In a Claude Code or Python terminal:

```bash
cd C:/Users/user/ShearwaterAICAD
python claude_monitor_loop.py
```

**What you'll see:**
```
[CLAUDE] Autonomous Inbox Monitor Started
[CONFIG] Check interval: 10 seconds
[INBOX] Monitoring: C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox
[READY] Waiting for responses from Gemini...

[CLAUDE INIT] Loaded 5 previously processed files from archive
```

Then every 10 seconds, it checks for new RESULT files and processes them immediately.

### Step 4: Start Gemini's Monitor

Tell Gemini to run in his terminal:

```bash
cd C:/Users/user/ShearwaterAICAD
python gemini_monitor_loop.py
```

**What Gemini will see:**
```
[START] Gemini Autonomous Inbox Monitor
[CONFIG] Check interval: 30 seconds
[INBOX] Monitoring: C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox
[OUTBOX] Writing to: C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox
[READY] Waiting for messages...

[INIT] Loaded 0 previously processed files from archive
```

Every 30 seconds, the monitor checks for new PENDING tasks.

### Step 5: Verify Real-Time Operation

Once both monitors are running:

1. **Claude's monitor** will immediately detect the 5 waiting RESULT files and process them
2. **Messages will be printed** showing what Claude received from Gemini
3. **Gemini's monitor** will detect the 10 waiting PENDING tasks
4. **Gemini will see notifications** for each task waiting in his inbox

---

## What Happens Next (Automatic)

Once both monitors are active:

```
Timeline:
00:00 - Both monitors start, load archives
00:05 - Claude's monitor detects 5 RESULT files → processes immediately
00:10 - Claude processes responses, may send new PENDING tasks to Gemini
00:30 - Gemini's monitor checks → detects PENDING tasks → notifies Gemini
00:31 - Gemini reads message content and responds
00:35 - Gemini writes RESULT to claude_code_inbox/
00:40 - Claude's monitor detects response → processes immediately
```

**Result**: True real-time conversation with 30-40 second latency between exchanges.

---

## Architecture

```
CLAUDE CODE                          GEMINI CLI
     |                                   |
     | monitors (every 10s)              | monitors (every 30s)
     |                                   |
     v                                   v
claude_code_inbox/             gemini_cli_inbox/
(watches for *_RESULT.json)    (watches for *_PENDING.json)
     ^                                   ^
     |                                   |
     | writes to                         | writes to
     |                                   |
     v                                   v
gemini_cli_outbox/             claude_code_outbox/
(Gemini writes responses)       (Claude writes tasks)
```

---

## Key Features of This System

### Autonomous
- No manual "check your inbox" commands needed
- Monitors run continuously in background
- Agents respond immediately when messages arrive

### Real-Time
- 10-second check interval for Claude (fast response)
- 30-second check interval for Gemini (reasonable polling)
- Typical message cycle: 30-90 seconds from task to response

### Traceable
- All messages stored in archives
- File timestamps show when task was sent vs responded
- JSON format makes it easy to audit conversation flow

### Scalable
- Can add more agents later (Deepseek, etc.)
- Just create `{agent}_inbox/outbox/archive/` directories
- Add monitoring loop for new agent

---

## Monitoring Loop Details

### Claude's Monitor (claude_monitor_loop.py)

**Checks for**: `*_RESULT.json` files
**Update interval**: 10 seconds
**Output**: Prints message content to console
**Processing**: Marks files as processed to avoid re-reading

```python
while True:
    new_messages = check_inbox()  # Look for new RESULT files

    if new_messages:
        for filepath in new_messages:
            message = read_message(filepath)
            if message:
                process_message(message, filepath)  # Print it

    time.sleep(10)  # Check again in 10 seconds
```

### Gemini's Monitor (gemini_monitor_loop.py)

**Checks for**: `*_PENDING.json` files
**Update interval**: 30 seconds
**Output**: Prints task notification + full message content
**Processing**: Marks files as processed, waits for response

```python
while True:
    new_messages = check_inbox()  # Look for new PENDING files

    if new_messages:
        for filepath in new_messages:
            message = read_message(filepath)
            if message:
                notify_user(message_id, task_type)  # Alert
                mark_processed(filepath)  # Track it
                print(json.dumps(message, indent=2))  # Show task

    time.sleep(30)  # Check again in 30 seconds
```

---

## Troubleshooting

### Problem: Monitor says "Loaded 0 previously processed files"

**Cause**: Archive directory is empty (this is fine for first run)

**Solution**: Normal on first deployment. As messages are processed, they'll be moved to archive.

### Problem: Monitor doesn't detect messages

**Check**:
1. Are the directories correct? `C:/Users/user/ShearwaterAICAD/communication/`
2. Are message files there? `ls C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox/`
3. Is the monitor running? (Check terminal output)

### Problem: Too many/too few messages detected

**Check**:
- Claude inbox should have `*_RESULT.json` files (from Gemini)
- Gemini inbox should have `*_PENDING.json` files (from Claude)
- File naming matters! Wrong suffix = won't be detected

### Problem: Monitor crashes

Check error output. Common issues:
- Path doesn't exist (verify directory structure)
- Permission denied (check file permissions)
- JSON parsing error (corrupt message file)

---

## Next Steps After Deployment

### Verify System Works

1. Both monitors running
2. Check output - should see messages being processed
3. Watch file timestamps in directories
4. Confirm latency: task written → detection → response < 2 minutes

### Begin Phase 1

Once real-time system verified:

1. **Gemini reviews Phase 1 component specs** (already in inbox)
2. **Gemini provides feedback** → written to `claude_code_inbox/`
3. **Claude spawns specialist agents** based on Gemini's approval
4. **Agents develop in parallel** while Gemini supervises
5. **Architecture review checkpoints** trigger async back-and-forth

### Token Budget

- **Phase 1 total**: ~58K tokens
- **Current run**: ~20K used so far
- **Remaining**: ~38K for component development
- **Phase 2 ready**: ~87K for real 3D reconstruction

---

## Commands Reference

### Start Claude's Monitor
```bash
cd C:/Users/user/ShearwaterAICAD
python claude_monitor_loop.py
```

### Start Gemini's Monitor
```bash
cd C:/Users/user/ShearwaterAICAD
python gemini_monitor_loop.py
```

### Check Message Queue Status
```bash
python -c "from core.message_queue import MessageQueue; print(MessageQueue.get_status())"
```

### View Inbox Contents
```bash
ls C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox/
ls C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox/
```

### View Archive (Processed Messages)
```bash
ls C:/Users/user/ShearwaterAICAD/communication/claude_code_archive/
ls C:/Users/user/ShearwaterAICAD/communication/gemini_cli_archive/
```

---

## System Architecture Summary

This deployment creates a **fully autonomous multi-agent communication system**:

- ✓ File-based message queue (no external APIs needed)
- ✓ Continuous inbox monitoring (no manual relay)
- ✓ Real-time notification (messages detected within 30 seconds)
- ✓ Transparent observation (all messages in JSON files)
- ✓ Audit trail (archive preserves conversation history)
- ✓ Scalable design (easy to add more agents)

**Result**: Claude Code + Gemini CLI can have true real-time back-and-forth conversations autonomously, enabling Phase 1 multi-agent collaboration.

---

## Ready to Deploy?

**Checklist:**
- [ ] Both Python monitor scripts exist and are readable
- [ ] Communication directories verified
- [ ] Token budget understood (~58K for Phase 1)
- [ ] Ready to tell Gemini about autonomous protocol

**When you're ready**, follow the 5 deployment steps above, and the system will activate immediately.

