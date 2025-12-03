"""
Context Checkpoint System - Auto-saves state when token budget <5%
Prevents data loss during context compaction
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ContextCheckpoint:
    """Manages automatic context snapshots to preserve state across compaction"""

    CHECKPOINT_DIR = Path("communication/context_checkpoints")
    TOKEN_BUDGET_THRESHOLD = 0.05  # 5%

    def __init__(self):
        self.checkpoint_dir = self.CHECKPOINT_DIR
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.last_checkpoint_file = self.checkpoint_dir / "LATEST_CHECKPOINT.json"

    def get_checkpoint_filename(self) -> str:
        """Generate timestamped checkpoint filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"CHECKPOINT_{timestamp}.json"

    def should_checkpoint(self, token_budget_percent: float) -> bool:
        """
        Determine if checkpoint needed based on token budget

        Args:
            token_budget_percent: Current token usage as percentage (0-1)

        Returns:
            True if token_budget_percent < 5%
        """
        return token_budget_percent < self.TOKEN_BUDGET_THRESHOLD

    def create_checkpoint(self, state: Dict[str, Any]) -> str:
        """
        Create and save a checkpoint file

        Args:
            state: Current system state to preserve

        Returns:
            Path to saved checkpoint file
        """
        checkpoint_data = {
            "timestamp": datetime.now().isoformat(),
            "token_budget_threshold_triggered": True,
            "state": state,
            "purpose": "Context preservation before compaction",
            "recovery_instructions": [
                "1. When context resumes, load this checkpoint",
                "2. Restore all state variables",
                "3. Re-initialize any running processes",
                "4. Continue from last known good state"
            ]
        }

        # Save timestamped checkpoint
        checkpoint_file = self.checkpoint_dir / self.get_checkpoint_filename()
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)

        # Also save as LATEST for quick access
        with open(self.last_checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2, default=str)

        return str(checkpoint_file)

    def load_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent checkpoint

        Returns:
            Checkpoint data if exists, None otherwise
        """
        if not self.last_checkpoint_file.exists():
            return None

        try:
            with open(self.last_checkpoint_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def list_checkpoints(self) -> list:
        """List all available checkpoints"""
        if not self.checkpoint_dir.exists():
            return []

        checkpoints = sorted(
            self.checkpoint_dir.glob("CHECKPOINT_*.json"),
            reverse=True
        )
        return [str(cp) for cp in checkpoints]

    def cleanup_old_checkpoints(self, keep_count: int = 5) -> None:
        """Keep only the N most recent checkpoints"""
        checkpoints = self.list_checkpoints()

        if len(checkpoints) > keep_count:
            for checkpoint in checkpoints[keep_count:]:
                try:
                    os.remove(checkpoint)
                except OSError:
                    pass


class ContextState:
    """Manages the current execution state for checkpointing"""

    def __init__(self):
        self.session_data = {}
        self.task_progress = {}
        self.agent_status = {}
        self.active_processes = []
        self.pending_tasks = []
        self.completed_tasks = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return {
            "session_data": self.session_data,
            "task_progress": self.task_progress,
            "agent_status": self.agent_status,
            "active_processes": self.active_processes,
            "pending_tasks": self.pending_tasks,
            "completed_tasks": self.completed_tasks,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Restore state from dictionary"""
        self.session_data = data.get("session_data", {})
        self.task_progress = data.get("task_progress", {})
        self.agent_status = data.get("agent_status", {})
        self.active_processes = data.get("active_processes", [])
        self.pending_tasks = data.get("pending_tasks", [])
        self.completed_tasks = data.get("completed_tasks", [])


def emergency_checkpoint(state: Dict[str, Any], token_budget_percent: float) -> None:
    """
    Emergency checkpoint trigger - called when token budget drops critically low

    Args:
        state: Current system state
        token_budget_percent: Token budget percentage (0-1)
    """
    checkpoint = ContextCheckpoint()

    if checkpoint.should_checkpoint(token_budget_percent):
        checkpoint_path = checkpoint.create_checkpoint(state)

        # Log the emergency
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "EMERGENCY_CHECKPOINT",
            "token_budget_percent": token_budget_percent,
            "checkpoint_saved": checkpoint_path,
            "message": f"Context compaction imminent. State saved to {checkpoint_path}"
        }

        # Append to emergency log
        emergency_log = Path("communication/context_checkpoints/EMERGENCY_LOG.json")
        try:
            if emergency_log.exists():
                with open(emergency_log, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(log_entry)

            with open(emergency_log, 'w') as f:
                json.dump(logs, f, indent=2)
        except (json.JSONDecodeError, IOError):
            pass


if __name__ == "__main__":
    # Test the checkpoint system
    checkpoint = ContextCheckpoint()
    state = ContextState()

    # Simulate some state
    state.session_data = {"frontend_rounds": 250, "status": "active"}
    state.task_progress = {"setup": 100, "websocket": 0}
    state.pending_tasks = ["WebSocket hook", "Message types", "Components"]

    # Create checkpoint
    path = checkpoint.create_checkpoint(state.to_dict())
    print(f"Checkpoint created: {path}")

    # List checkpoints
    checkpoints = checkpoint.list_checkpoints()
    print(f"Available checkpoints: {len(checkpoints)}")

    # Load latest
    latest = checkpoint.load_latest_checkpoint()
    print(f"Latest checkpoint timestamp: {latest['timestamp'] if latest else 'None'}")
