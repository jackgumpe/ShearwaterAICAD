"""
Context Recovery - Initializes Claude Code after compaction/context reset
Loads checkpoint and restores state automatically
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class ContextRecovery:
    """Handles automatic recovery after context compaction"""

    CHECKPOINT_DIR = Path("communication/context_checkpoints")
    LATEST_CHECKPOINT = CHECKPOINT_DIR / "LATEST_CHECKPOINT.json"

    @classmethod
    def has_checkpoint(cls) -> bool:
        """Check if a checkpoint file exists"""
        return cls.LATEST_CHECKPOINT.exists()

    @classmethod
    def load_checkpoint(cls) -> Optional[Dict[str, Any]]:
        """Load the latest checkpoint"""
        if not cls.has_checkpoint():
            return None

        try:
            with open(cls.LATEST_CHECKPOINT, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    @classmethod
    def get_recovery_summary(cls) -> Optional[str]:
        """Get human-readable recovery summary"""
        checkpoint = cls.load_checkpoint()
        if not checkpoint:
            return None

        state = checkpoint.get('state', {})
        timestamp = checkpoint.get('timestamp', 'unknown')

        summary = f"""
CONTEXT RECOVERY LOADED
========================
Checkpoint Time: {timestamp}
State Restored: Yes

Key State:
- Session Data: {state.get('session_data', {})}
- Task Progress: {state.get('task_progress', {})}
- Agent Status: {state.get('agent_status', {})}
- Pending Tasks: {len(state.get('pending_tasks', []))} items
- Completed Tasks: {len(state.get('completed_tasks', []))} items

NOTE: All state has been restored. Continue from where you left off.
"""
        return summary

    @classmethod
    def print_recovery_info(cls) -> bool:
        """Print recovery info if available. Returns True if recovery loaded."""
        if not cls.has_checkpoint():
            return False

        print(cls.get_recovery_summary())
        return True

    @classmethod
    def get_context_instructions(cls) -> str:
        """Get instructions for Claude Code to follow after recovery"""
        checkpoint = cls.load_checkpoint()

        if checkpoint:
            return f"""INSTRUCTIONS FOR CLAUDE CODE AFTER CONTEXT RECOVERY:

1. You have recovered from a context compaction
2. Checkpoint loaded from: {cls.LATEST_CHECKPOINT}
3. Timestamp: {checkpoint.get('timestamp')}
4. State has been fully preserved

CRITICAL: Review the state and:
- Verify all pending tasks from before compaction
- Check agent status to see what was in progress
- Resume the Frontend 250-round execution if still pending
- Do NOT restart completed tasks

Current pending tasks: {checkpoint.get('state', {}).get('pending_tasks', [])}
In progress when compacted: {checkpoint.get('state', {}).get('task_progress', {})}

Continue seamlessly with no interruption to workflow."""
        else:
            return "No checkpoint found. This is a fresh start."


def initialize_recovery():
    """Call this at the start of any Claude Code session"""
    recovery = ContextRecovery()

    if recovery.has_checkpoint():
        print("=" * 60)
        print("CONTEXT CHECKPOINT DETECTED - RECOVERING STATE")
        print("=" * 60)
        recovery.print_recovery_info()
        return recovery.load_checkpoint()
    else:
        print("No context checkpoint. Starting fresh.")
        return None


if __name__ == "__main__":
    # Test recovery
    checkpoint = initialize_recovery()
    if checkpoint:
        print("\nCheckpoint loaded successfully")
        print(json.dumps(checkpoint, indent=2)[:500])  # Print first 500 chars
    else:
        print("No checkpoint to load")
