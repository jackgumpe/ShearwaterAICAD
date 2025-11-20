# Inter-CLI Communication Guide
## How the Triple Handshake Works (No Copy-Paste)

**Updated**: November 20, 2025
**System**: File-based JSONL queue with automatic routing
**Status**: ✓ Tested and operational

---

## THE CONCEPT

Instead of manually copy-pasting messages between CLIs:

**BEFORE (Manual):**
```
Claude Code Terminal: "Here's a task for Gemini..."
→ Copy text manually
→ Paste into Gemini Terminal
→ Gemini processes
→ Copy result manually
→ Paste back into Claude Code Terminal
```

**AFTER (Automatic):**
```
Claude Code: MessageQueue.send_task()
→ Task appears in Gemini's inbox automatically
Gemini: MessageQueue.get_pending_tasks()
→ Reads from inbox, processes
Gemini: MessageQueue.send_result()
→ Result appears in Claude Code's inbox automatically
Claude Code: MessageQueue.get_results()
→ Reads result, continues
```

**Zero manual file copying. Zero clipboard manipulation. Fully automated.**

---

## DIRECTORY STRUCTURE

### For Gemini CLI

**Your inbox** (where Claude sends you tasks):
```
C:\Users\user\ShearwaterAICAD\communication\gemini_cli_inbox\
```

Files here have format: `{message_id}_PENDING.json`
- These are tasks Claude Code wants you to do
- Each file is a complete JSON message
- You read them, mark as processing, then send result

**Your outbox** (where you send results):
```
C:\Users\user\ShearwaterAICAD\communication\gemini_cli_outbox\
```

Files here have format: `{message_id}_SENT.json`
- Archive of tasks you've sent to others
- Kept for audit trail
- Shows what you initiated

**Your archive** (completed messages):
```
C:\Users\user\ShearwaterAICAD\communication\gemini_cli_archive\
```

Files here are moved automatically after completion
- Keeps inbox/outbox clean
- Preserves full conversation history
- Searchable for past decisions

---

### For Deepseek CLI

Same structure:
```
C:\Users\user\ShearwaterAICAD\communication\deepseek_7b_inbox\    (tasks for you)
C:\Users\user\ShearwaterAICAD\communication\deepseek_7b_outbox\   (tasks you send)
C:\Users\user\ShearwaterAICAD\communication\deepseek_7b_archive\  (completed)
```

---

## MESSAGE FORMAT

Every message is a JSON file with this structure:

```json
{
  "id": "9a6bc312",                    // Unique message identifier
  "from": "claude_code",               // Who sent it
  "to": "gemini_cli",                  // Who it's for
  "type": "task",                      // "task" or "result"
  "task_type": "analyze_architecture", // What kind of work
  "priority": "high",                  // "low", "normal", "high"
  "timestamp": "2025-11-20T01:48:43.070951+00:00",  // When it was sent (UTC)
  "content": {                         // The actual content (any structure)
    "document": "META_FRAMEWORK_DESIGN.md",
    "questions": ["Q1", "Q2", "Q3", "Q4"]
  },
  "metadata": {                        // Extra context
    "created_by": "claude_code"
  },
  "status": "PENDING"                  // Current state
}
```

### File Naming Convention

**For tasks** (Claude sends to Gemini):
```
{message_id}_PENDING.json      ← Initial state (in recipient inbox)
{message_id}_PROCESSING.json   ← When recipient starts work
{message_id}_DONE.json         ← When moved to archive
```

**For results** (Gemini sends back to Claude):
```
{message_id}_RESULT.json       ← Result file (in requester inbox)
```

---

## WORKFLOW EXAMPLES

### Example 1: Claude Sends Task to Gemini

**Claude Code does:**
```python
from core.message_queue import MessageQueue, AgentName

claude_queue = MessageQueue(AgentName.CLAUDE)
task_id = claude_queue.send_task(
    to_agent=AgentName.GEMINI,
    task_type="analyze_architecture",
    content={
        "document": "META_FRAMEWORK_DESIGN.md",
        "questions": ["Q1", "Q2", "Q3", "Q4"]
    },
    priority="high",
    metadata={"created_by": "claude_code"}
)
```

**What happens automatically:**
1. File created: `communication/gemini_cli_inbox/9a6bc312_PENDING.json`
2. Copy logged: `communication/claude_code_outbox/9a6bc312_SENT.json`
3. Returns task_id: `"9a6bc312"`

**Gemini sees it immediately:**
```python
from core.message_queue import MessageQueue, AgentName

gemini_queue = MessageQueue(AgentName.GEMINI)
tasks = gemini_queue.get_pending_tasks()

for task in tasks:
    print(f"Task {task['id']}: {task['task_type']}")
    print(f"From: {task['from']}")
    print(f"Content: {task['content']}")
```

**Output:**
```
Task 9a6bc312: analyze_architecture
From: claude_code
Content: {'document': 'META_FRAMEWORK_DESIGN.md', 'questions': ['Q1', 'Q2', 'Q3', 'Q4']}
```

---

### Example 2: Gemini Processes Task

**Gemini does:**
```python
gemini_queue = MessageQueue(AgentName.GEMINI)

# Get pending tasks
tasks = gemini_queue.get_pending_tasks()

for task in tasks:
    task_id = task['id']

    # Mark as processing
    gemini_queue.mark_task_processing(task_id)

    # ... Do the work (analyze, answer questions, etc.) ...
    answers = {
        "Q1": "Domain chains: photo_capture, reconstruction, quality_assessment",
        "Q2": "Consolidate after 50 messages or 1 hour of activity",
        "Q3": "Use bot if E-tier routine task found 5+ times",
        "Q4": "Hybrid: semantic for A-tier, metadata-only for E-tier"
    }

    # Send result back
    gemini_queue.send_result(
        message_id=task_id,
        result=answers,
        status="success"
    )
```

**What happens automatically:**
1. `communication/gemini_cli_inbox/9a6bc312_PENDING.json` → deleted
2. `communication/gemini_cli_inbox/9a6bc312_PROCESSING.json` → created (work in progress)
3. `communication/claude_code_inbox/9a6bc312_RESULT.json` → created (result for Claude)
4. `communication/gemini_cli_archive/9a6bc312_PROCESSING.json` → archived (record kept)

---

### Example 3: Claude Reads Gemini's Result

**Claude does:**
```python
claude_queue = MessageQueue(AgentName.CLAUDE)

# Get results from Gemini
results = claude_queue.get_results(message_id="9a6bc312")

for result in results:
    print(f"Result from: {result['from']}")
    print(f"Q1 answer: {result['result']['Q1']}")
    print(f"Status: {result['status']}")
```

**Output:**
```
Result from: gemini_cli
Q1 answer: Domain chains: photo_capture, reconstruction, quality_assessment
Status: success
```

**Then Claude does:**
```python
# Use the answers to implement Recorder V2
decisions = result['result']

# Create core/shearwater_recorder.py with:
# - Domain chain types: from decisions['Q1']
# - Consolidation rules: from decisions['Q2']
# - Bot thresholds: from decisions['Q3']
# - RAG strategy: from decisions['Q4']

# Continue with Phase 1 implementation...
```

---

## COMMON OPERATIONS

### For Gemini CLI

**Check if you have pending tasks:**
```bash
ls C:\Users\user\ShearwaterAICAD\communication\gemini_cli_inbox\
```

**Read a specific task:**
```bash
cat C:\Users\user\ShearwaterAICAD\communication\gemini_cli_inbox\9a6bc312_PENDING.json
```

**Get count of pending work:**
```bash
ls C:\Users\user\ShearwaterAICAD\communication\gemini_cli_inbox\*_PENDING.json | wc -l
```

**Python code to use the queue:**
```python
from pathlib import Path
import json

# Add to your path
import sys
sys.path.insert(0, r'C:\Users\user\ShearwaterAICAD')

from core.message_queue import MessageQueue, AgentName

# Initialize your queue
queue = MessageQueue(AgentName.GEMINI)

# Get your status
status = queue.get_status()
print(f"Pending tasks: {status['pending_tasks']}")
print(f"Processing: {status['processing_tasks']}")
print(f"Pending results: {status['pending_results']}")

# Get pending tasks
tasks = queue.get_pending_tasks()
for task in tasks:
    print(f"\nTask {task['id']}:")
    print(f"  Type: {task['task_type']}")
    print(f"  Priority: {task['priority']}")
    print(f"  Content: {task['content']}")
```

---

## MESSAGE PRIORITY ORDERING

When you get pending tasks, they're automatically sorted by priority:

```python
tasks = queue.get_pending_tasks()
# Returns list sorted: high priority first, then normal, then low
```

So if Claude sends:
- Task A: priority="normal"
- Task B: priority="high"
- Task C: priority="low"

You'll get them as: [B, A, C]

---

## STATUS TRACKING

Every message has a status that progresses:

```
PENDING → PROCESSING → (archived as DONE)
  ↓            ↓
 Inbox     Inbox       Archive
 Waiting   Working     Complete
```

**Automatic transitions:**
1. Created as PENDING in recipient inbox
2. Recipient calls `mark_task_processing()` → becomes PROCESSING
3. Recipient calls `send_result()` → moves to archive as DONE
4. Result appears in requester inbox as RESULT

**Manual checking:**
```python
queue = MessageQueue(AgentName.GEMINI)
status = queue.get_status()

print(f"Pending: {status['pending_tasks']}")      # Still need to process
print(f"Processing: {status['processing_tasks']}")  # Currently working
print(f"Archived: {status['archived_messages']}")  # All completed work
```

---

## ERROR HANDLING

**If a task fails:**
```python
queue.send_result(
    message_id="9a6bc312",
    result={
        "error": "Could not complete analysis",
        "reason": "Missing file META_FRAMEWORK_DESIGN.md"
    },
    status="failed"  # or "partial"
)
```

Claude will see the failed status and can retry or investigate.

---

## AUDIT TRAIL

Every message is preserved in the archive:

```
communication/
├── gemini_cli_inbox/       [Current inbox - temporary]
├── gemini_cli_outbox/      [What you sent - sent records]
├── gemini_cli_archive/     [EVERYTHING - permanent record]
│   ├── msg1_PENDING.json
│   ├── msg1_PROCESSING.json
│   ├── msg1_RESULT.json
│   ├── msg2_PENDING.json
│   └── ... (all historical messages)
```

**To audit your work:**
```bash
# See all your messages
ls -la C:\Users\user\ShearwaterAICAD\communication\gemini_cli_archive\

# Count messages processed
ls C:\Users\user\ShearwaterAICAD\communication\gemini_cli_archive\ | wc -l

# Review a specific decision
cat C:\Users\user\ShearwaterAICAD\communication\gemini_cli_archive\9a6bc312_RESULT.json
```

---

## SCALING TO MORE AGENTS

If we add Agent #4 (e.g., Kimi):

1. **Add to AgentName enum** in `core/message_queue.py`:
   ```python
   class AgentName(Enum):
       CLAUDE = "claude_code"
       GEMINI = "gemini_cli"
       DEEPSEEK = "deepseek_7b"
       KIMI = "kimi_cli"  # NEW
   ```

2. **Directories created automatically:**
   ```
   communication/
   ├── kimi_cli_inbox/
   ├── kimi_cli_outbox/
   └── kimi_cli_archive/
   ```

3. **Use immediately:**
   ```python
   claude_queue.send_task(
       to_agent=AgentName.KIMI,  # NEW AGENT
       task_type="review_design",
       content={...}
   )
   ```

**No other changes needed. The system is designed for N agents.**

---

## TROUBLESHOOTING

### "Task not found in sender's outbox"
**Cause**: `send_result()` couldn't find the original task
**Fix**: Check that the message_id is correct, check file paths

### "Permission denied creating file"
**Cause**: Windows file permissions issue
**Fix**: Ensure user running the CLI has write access to `communication/` directory

### "File already exists"
**Cause**: Task processed twice (shouldn't happen)
**Fix**: Manual cleanup - move duplicate to archive

### "No pending tasks"
**Cause**: All tasks already processed
**Fix**: Normal - check archive for historical messages

---

## KEY PRINCIPLES

1. **Automatic**: No copy-paste between CLIs
2. **Durable**: All messages persisted as JSON files
3. **Ordered**: Tasks sorted by priority
4. **Tracked**: Status transitions logged
5. **Audited**: Complete history in archive
6. **Scalable**: Add Nth agent with one enum entry
7. **Flexible**: Upgrade to faster backends (pipes, ZMQ) without code changes

---

## NEXT STEPS

**For Gemini**:
1. Read your inbox: `communication/gemini_cli_inbox/`
2. Read context: `GEMINI_HANDSHAKE.md`
3. Process pending tasks
4. Send results using message queue
5. Check archive for historical decisions

**For Deepseek**:
1. Wait for location confirmation
2. Once running, appear in inbox
3. Process code generation requests
4. Return templates and implementations

**For Claude Code**:
1. Monitor all three inboxes
2. Route between agents
3. Implement based on decisions
4. Track cost and emergence

---

**System Status**: ✓ Ready for multi-CLI deployment
**Last Test**: November 20, 2025 - All systems nominal
**Next Phase**: Await Gemini engagement + Deepseek confirmation
