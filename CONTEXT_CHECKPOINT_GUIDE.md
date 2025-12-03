# Context Checkpoint System - Implementation Guide

## Problem
When Claude Code context gets compacted, there's a gap where short-medium memory/context is lost. This system prevents that by auto-saving state when token budget drops below 5%.

## Solution Architecture

### Three Core Components

#### 1. **ContextCheckpoint** (`src/core/context_checkpoint.py`)
- Monitors token budget percentage
- Saves JSON snapshots when <5% budget remains
- Maintains LATEST_CHECKPOINT.json for quick access
- Keeps timestamped backup files
- Auto-cleans old checkpoints (keeps last 5)

#### 2. **ClaudeContextMonitor** (`src/core/claude_context_monitor.py`)
- Integrates into Claude Code's message loop
- Checks token budget at 5-second intervals
- Triggers emergency checkpoint
- Writes notices to agent inbox

#### 3. **ContextRecovery** (`src/core/context_recovery.py`)
- Loads checkpoint after context reset
- Prints recovery summary
- Provides instructions for resuming work
- Ensures no duplicate task execution

## Integration Steps

### Step 1: Add to Claude Code Message Loop
In your Claude Code session initialization:

```python
from src.core.context_recovery import initialize_recovery

# At session start
checkpoint = initialize_recovery()
if checkpoint:
    print("State recovered from checkpoint")
```

### Step 2: Monitor Token Budget
Every few operations, report token usage:

```python
from src.core.claude_context_monitor import report_token_budget

# When you notice token budget getting low
token_percent = 0.042  # From Claude Code's environment
current_state = {
    "frontend_rounds": 120,
    "tasks_completed": ["websocket", "types"],
    "pending_tasks": ["components", "integration"]
}

report_token_budget(token_percent, current_state)
```

### Step 3: Handle Checkpoint Notices
Agents will find notices in `communication/claude_code_inbox/CONTEXT_CHECKPOINT_NOTICE.json`

Example notice:
```json
{
  "timestamp": "2025-12-03T12:45:00",
  "type": "context_checkpoint_notice",
  "priority": "CRITICAL",
  "message": "Context compaction imminent. Checkpoint saved.",
  "checkpoint_location": "communication/context_checkpoints/LATEST_CHECKPOINT.json",
  "action": "Load checkpoint and continue from saved state"
}
```

## Usage

### Manual Checkpoint Creation
```python
from src.core.context_checkpoint import ContextCheckpoint, ContextState

checkpoint = ContextCheckpoint()
state = ContextState()

# Populate state
state.session_data = {"frontend_rounds": 250, "status": "active"}
state.pending_tasks = ["WebSocket hook", "Message types"]

# Save
path = checkpoint.create_checkpoint(state.to_dict())
print(f"Saved to {path}")
```

### Automatic Monitoring
```python
from src.core.claude_context_monitor import report_token_budget

# Claude Code monitors automatically when you call this
report_token_budget(0.042)  # 4.2% remaining - triggers checkpoint
```

### Recovery After Compaction
```python
from src.core.context_recovery import ContextRecovery

recovery = ContextRecovery()
if recovery.has_checkpoint():
    checkpoint_data = recovery.load_checkpoint()
    print(recovery.get_recovery_summary())
```

## Checkpoint File Structure

### LATEST_CHECKPOINT.json
```json
{
  "timestamp": "2025-12-03T12:45:00Z",
  "token_budget_threshold_triggered": true,
  "state": {
    "session_data": {...},
    "task_progress": {...},
    "agent_status": {...},
    "active_processes": [...],
    "pending_tasks": [...],
    "completed_tasks": [...]
  },
  "purpose": "Context preservation before compaction",
  "recovery_instructions": [...]
}
```

### Checkpoint Storage
- **Location**: `communication/context_checkpoints/`
- **Latest**: `LATEST_CHECKPOINT.json` (always current)
- **Archives**: `CHECKPOINT_YYYYMMDD_HHMMSS.json` (timestamped backups)
- **Emergency Log**: `EMERGENCY_LOG.json` (all compaction events)

## Key Features

✅ **Automatic Trigger**: No manual action needed - triggers at <5% token budget
✅ **Fast Recovery**: Checkpoint loaded immediately after context reset
✅ **No Data Loss**: All state preserved between compactions
✅ **Task Continuity**: Tasks resume from exact point where stopped
✅ **Auto-Cleanup**: Old checkpoints automatically removed (keeps 5 recent)
✅ **Emergency Log**: Track all compaction events for debugging

## Testing

Run the test to verify the system works:

```bash
cd C:\Users\user\ShearwaterAICAD
python -m src.core.context_checkpoint
python -m src.core.claude_context_monitor
python -m src.core.context_recovery
```

Expected output:
```
Checkpoint created: communication/context_checkpoints/CHECKPOINT_20251203_124500.json
Available checkpoints: 1
Latest checkpoint timestamp: 2025-12-03T12:45:00Z

Testing context monitor...
Threshold: 5.0%
Status: Normal (45%)
Status: Critical (4.2%) - Checkpoint triggered

Recovery message:
CONTEXT RECOVERY: Previous checkpoint loaded.
Timestamp: 2025-12-03T12:45:00Z
```

## For Claude Code Implementation

When integrating this into Claude Code directly:

1. **At startup**: Load recovery checkpoint if exists
2. **During execution**: Report token budget every few operations
3. **At context threshold**: System auto-saves state
4. **After compaction**: Recovery loads saved state
5. **Continue**: Resume work with full context restored

This prevents the memory gap that occurs during context compaction.

## Future Enhancements

- Real-time token budget tracking
- Granular state snapshots (per-task)
- Compression for large states
- Cloud backup option
- State diff tracking (only save changes)
