"""
Claude Code Context Monitor - Integrates with Claude Code to auto-checkpoint
Monitors token budget and triggers emergency checkpoint when <5%
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable
from src.core.context_checkpoint import ContextCheckpoint, emergency_checkpoint


class ClaudeContextMonitor:
    """
    Monitors Claude's context/token budget and triggers checkpoints

    This is integrated into Claude Code's message loop to detect token pressure
    and save state before context compaction occurs.
    """

    def __init__(self):
        self.checkpoint = ContextCheckpoint()
        self.monitoring = False
        self.last_check_time = 0
        self.check_interval = 5  # Check every 5 seconds
        self.checkpoint_threshold = 0.05  # 5%
        self.emergency_triggered = False

    def check_token_budget(self, token_budget_percent: float) -> bool:
        """
        Check if emergency checkpoint needed

        Args:
            token_budget_percent: Token usage as decimal (0-1)

        Returns:
            True if checkpoint was triggered
        """
        current_time = time.time()

        # Don't check more than check_interval seconds
        if current_time - self.last_check_time < self.check_interval:
            return False

        self.last_check_time = current_time

        if token_budget_percent < self.checkpoint_threshold:
            self.emergency_triggered = True
            return True

        return False

    def on_context_low(self, current_state: dict) -> str:
        """
        Execute when context is critically low

        Args:
            current_state: Current system state to preserve

        Returns:
            Path to saved checkpoint
        """
        return self.checkpoint.create_checkpoint(current_state)

    def get_recovery_prompt(self) -> Optional[str]:
        """
        Get checkpoint recovery prompt to include in next message

        Returns:
            Recovery prompt if checkpoint exists, None otherwise
        """
        latest = self.checkpoint.load_latest_checkpoint()
        if not latest:
            return None

        return f"""CONTEXT RECOVERY: Previous checkpoint loaded.
Timestamp: {latest.get('timestamp')}
Previous state preserved. Continue from last known state.
See communication/context_checkpoints/LATEST_CHECKPOINT.json for full state."""

    def write_checkpoint_directive(self, message: str) -> None:
        """
        Write a checkpoint directive for the agents to read

        Args:
            message: Message to include in directive
        """
        directive = {
            "timestamp": datetime.now().isoformat(),
            "type": "context_checkpoint_notice",
            "priority": "CRITICAL",
            "message": message,
            "checkpoint_location": str(self.checkpoint.last_checkpoint_file),
            "action": "Load checkpoint and continue from saved state"
        }

        outbox = Path("communication/claude_code_inbox/CONTEXT_CHECKPOINT_NOTICE.json")
        outbox.parent.mkdir(parents=True, exist_ok=True)

        with open(outbox, 'w') as f:
            json.dump(directive, f, indent=2)


class ContextTokenMonitor:
    """
    Simple hook to be called with token budget information
    Can be imported and used by Claude Code itself
    """

    def __init__(self):
        self.monitor = ClaudeContextMonitor()

    def report_token_budget(self, token_budget_percent: float, current_state: Optional[dict] = None) -> None:
        """
        Called by Claude Code to report current token budget

        Args:
            token_budget_percent: Current token usage (0-1)
            current_state: Optional current state to save
        """
        if self.monitor.check_token_budget(token_budget_percent):
            if current_state is None:
                current_state = self._build_default_state()

            checkpoint_path = self.monitor.on_context_low(current_state)

            # Write notice for agents
            self.monitor.write_checkpoint_directive(
                f"Context compaction imminent. Checkpoint saved to {checkpoint_path}"
            )

            print(f"\n[EMERGENCY] Context budget critical ({token_budget_percent*100:.1f}%)")
            print(f"[CHECKPOINT] State saved to {checkpoint_path}")

    def _build_default_state(self) -> dict:
        """Build default state if none provided"""
        return {
            "frontend_status": "250 rounds in progress",
            "grant_emails": "16/16 sent - awaiting responses",
            "gluade": "paused - focus on frontend",
            "checkpoint_reason": "token_budget_critical"
        }


# Global instance for easy access
_global_monitor = ContextTokenMonitor()


def report_token_budget(token_budget_percent: float, current_state: Optional[dict] = None) -> None:
    """
    Global function to call from Claude Code

    Usage in Claude Code:
        from src.core.claude_context_monitor import report_token_budget
        report_token_budget(0.042)  # 4.2% remaining
    """
    _global_monitor.report_token_budget(token_budget_percent, current_state)


def get_recovery_message() -> Optional[str]:
    """Get recovery message if checkpoint exists"""
    return _global_monitor.monitor.get_recovery_prompt()


if __name__ == "__main__":
    # Test the monitor
    monitor = ContextTokenMonitor()

    print("Testing context monitor...")
    print(f"Threshold: {monitor.monitor.checkpoint_threshold * 100}%")

    # Simulate normal operation
    monitor.report_token_budget(0.45)  # 45% - normal
    print("Status: Normal (45%)")

    # Simulate low context
    monitor.report_token_budget(0.042)  # 4.2% - critical
    print("Status: Critical (4.2%) - Checkpoint triggered")

    # Check recovery message
    recovery = get_recovery_message()
    if recovery:
        print(f"\nRecovery message:\n{recovery}")
