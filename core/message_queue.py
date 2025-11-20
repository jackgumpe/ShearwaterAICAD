"""
Inter-CLI Communication System
Enables Claude Code, Gemini CLI, and Deepseek to communicate without copy-paste

Uses file-based JSONL queues with status tracking
Can be upgraded to named pipes or sockets later
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
from enum import Enum
import sys

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AgentName(Enum):
    """Agent identifiers for routing messages"""
    CLAUDE = "claude_code"
    GEMINI = "gemini_cli"
    DEEPSEEK = "deepseek_7b"


class MessageType(Enum):
    """Types of messages between agents"""
    TASK = "task"
    RESULT = "result"
    QUESTION = "question"
    STATUS = "status"
    DECISION = "decision"
    ERROR = "error"


class MessageQueue:
    """
    File-based message queue for inter-CLI communication

    Each agent has:
    - inbox/  - incoming messages
    - outbox/ - outgoing messages
    - archive/ - processed messages (for audit trail)

    File naming: {message_id}_{type}_{status}.json
    Status: PENDING → PROCESSING → DONE or FAILED
    """

    def __init__(self, agent_name: AgentName, base_path: Optional[Path] = None):
        """Initialize message queue for an agent"""
        if base_path is None:
            base_path = Path("C:/Users/user/ShearwaterAICAD/communication")

        self.agent_name = agent_name
        self.base_path = base_path
        self.inbox_path = base_path / f"{agent_name.value}_inbox"
        self.outbox_path = base_path / f"{agent_name.value}_outbox"
        self.archive_path = base_path / f"{agent_name.value}_archive"

        # Create directories
        for path in [self.inbox_path, self.outbox_path, self.archive_path]:
            path.mkdir(parents=True, exist_ok=True)

    def send_task(
        self,
        to_agent: AgentName,
        task_type: str,
        content: Dict,
        priority: str = "normal",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Send a task to another agent

        Args:
            to_agent: Recipient agent
            task_type: Type of task (e.g., "implement_recorder", "review_code")
            content: Task content/details
            priority: "low", "normal", "high"
            metadata: Optional metadata (context, references, etc.)

        Returns:
            message_id - for tracking
        """
        message_id = str(uuid.uuid4())[:8]

        message = {
            "id": message_id,
            "from": self.agent_name.value,
            "to": to_agent.value,
            "type": MessageType.TASK.value,
            "task_type": task_type,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": content,
            "metadata": metadata or {},
            "status": "PENDING"
        }

        # Write to recipient's inbox
        recipient_inbox = self.base_path / f"{to_agent.value}_inbox"
        recipient_inbox.mkdir(parents=True, exist_ok=True)

        filepath = recipient_inbox / f"{message_id}_PENDING.json"
        self._write_json(filepath, message)

        # Log to own outbox
        own_outbox_file = self.outbox_path / f"{message_id}_SENT.json"
        self._write_json(own_outbox_file, message)

        return message_id

    def send_result(
        self,
        message_id: str,
        result: Dict,
        status: str = "success"
    ) -> bool:
        """
        Send result back to task requester

        Args:
            message_id: Original task message ID
            result: Result content/output
            status: "success", "partial", "failed"

        Returns:
            True if sent successfully
        """
        try:
            # Read original message from outbox to find sender
            original_file = None
            for f in self.outbox_path.glob(f"{message_id}_*.json"):
                original_file = f
                break

            if not original_file:
                return False

            original_msg = self._read_json(original_file)
            sender = original_msg["from"]

            result_msg = {
                "id": message_id,
                "from": self.agent_name.value,
                "to": sender,
                "type": MessageType.RESULT.value,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "result": result
            }

            # Write to sender's inbox
            sender_inbox = self.base_path / f"{sender}_inbox"
            sender_inbox.mkdir(parents=True, exist_ok=True)

            result_file = sender_inbox / f"{message_id}_RESULT.json"
            self._write_json(result_file, result_msg)

            # Archive original
            self._archive_file(original_file)

            return True

        except Exception as e:
            print(f"Error sending result: {e}")
            return False

    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks for this agent"""
        tasks = []
        for task_file in self.inbox_path.glob("*_PENDING.json"):
            try:
                task = self._read_json(task_file)
                tasks.append(task)
            except Exception:
                pass
        return sorted(tasks, key=lambda x: x.get("priority") == "high", reverse=True)

    def get_results(self, message_id: Optional[str] = None) -> List[Dict]:
        """Get results for completed tasks"""
        results = []
        pattern = f"{message_id}_RESULT.json" if message_id else "*_RESULT.json"
        for result_file in self.inbox_path.glob(pattern):
            try:
                result = self._read_json(result_file)
                results.append(result)
            except Exception:
                pass
        return results

    def mark_task_processing(self, message_id: str) -> bool:
        """Mark a task as being processed"""
        try:
            pending_file = self.inbox_path / f"{message_id}_PENDING.json"
            if not pending_file.exists():
                return False

            message = self._read_json(pending_file)
            message["status"] = "PROCESSING"
            message["started_at"] = datetime.now(timezone.utc).isoformat()

            processing_file = self.inbox_path / f"{message_id}_PROCESSING.json"
            self._write_json(processing_file, message)
            pending_file.unlink()

            return True
        except Exception:
            return False

    def mark_task_complete(self, message_id: str) -> bool:
        """Mark a task as complete (after sending result)"""
        try:
            processing_file = self.inbox_path / f"{message_id}_PROCESSING.json"
            if processing_file.exists():
                self._archive_file(processing_file)
                return True
            return False
        except Exception:
            return False

    def get_status(self) -> Dict:
        """Get queue status"""
        return {
            "agent": self.agent_name.value,
            "pending_tasks": len(list(self.inbox_path.glob("*_PENDING.json"))),
            "processing_tasks": len(list(self.inbox_path.glob("*_PROCESSING.json"))),
            "pending_results": len(list(self.inbox_path.glob("*_RESULT.json"))),
            "archived_messages": len(list(self.archive_path.glob("*.json")))
        }

    @staticmethod
    def _write_json(filepath: Path, data: Dict) -> None:
        """Write JSON to file atomically"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _read_json(filepath: Path) -> Dict:
        """Read JSON from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _archive_file(self, filepath: Path) -> None:
        """Move a file to archive"""
        archive_file = self.archive_path / filepath.name
        filepath.rename(archive_file)


class HandshakeManager:
    """
    Manages initial handshake between three agents
    Ensures all agents are alive and ready to communicate
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("C:/Users/user/ShearwaterAICAD/communication")
        self.handshake_file = self.base_path / "handshake.json"

    def initialize(self) -> Dict:
        """Create initial handshake file"""
        now = datetime.now(timezone.utc).isoformat()
        handshake = {
            "initialized_at": now,
            "agents": {
                AgentName.CLAUDE.value: {
                    "status": "ready",
                    "last_seen": now,
                    "role": "Infrastructure & System Architecture"
                },
                AgentName.GEMINI.value: {
                    "status": "waiting",
                    "last_seen": None,
                    "role": "Creative Problem-Solving & Design"
                },
                AgentName.DEEPSEEK.value: {
                    "status": "waiting",
                    "last_seen": None,
                    "role": "Rapid Implementation & Code Generation"
                }
            },
            "protocol": "file-based_jsonl_queue_v1",
            "can_upgrade_to": ["named_pipes", "zeromq_sockets"]
        }

        self.base_path.mkdir(parents=True, exist_ok=True)
        with open(self.handshake_file, 'w', encoding='utf-8') as f:
            json.dump(handshake, f, indent=2)

        return handshake

    def agent_ready(self, agent_name: AgentName) -> bool:
        """Mark agent as ready"""
        try:
            with open(self.handshake_file, 'r', encoding='utf-8') as f:
                handshake = json.load(f)

            handshake["agents"][agent_name.value]["status"] = "ready"
            handshake["agents"][agent_name.value]["last_seen"] = datetime.now(timezone.utc).isoformat()

            with open(self.handshake_file, 'w', encoding='utf-8') as f:
                json.dump(handshake, f, indent=2)

            return True
        except Exception:
            return False

    def get_status(self) -> Dict:
        """Get handshake status"""
        try:
            with open(self.handshake_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def all_ready(self) -> bool:
        """Check if all agents are ready"""
        status = self.get_status()
        if not status.get("agents"):
            return False
        return all(
            agent.get("status") == "ready"
            for agent in status["agents"].values()
        )


def setup_communication_infrastructure() -> bool:
    """
    Initialize the entire communication infrastructure
    Call this once at startup
    """
    try:
        # Create base directory
        base_path = Path("C:/Users/user/ShearwaterAICAD/communication")
        base_path.mkdir(parents=True, exist_ok=True)

        # Initialize handshake
        handshake = HandshakeManager(base_path)
        handshake.initialize()

        # Create subdirectories for each agent
        for agent in AgentName:
            for subdir in ["inbox", "outbox", "archive"]:
                (base_path / f"{agent.value}_{subdir}").mkdir(parents=True, exist_ok=True)

        print("[OK] Communication infrastructure initialized")
        print(f"[OK] Base path: {base_path}")
        print("[OK] Queues ready for: claude_code, gemini_cli, deepseek_7b")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to initialize communication: {e}")
        return False


if __name__ == "__main__":
    # Test the system
    setup_communication_infrastructure()

    # Example: Claude sends a task to Gemini
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
    print(f"\n[SENT] Task to Gemini: {task_id}")
    print(f"[CHECK] C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox/{task_id}_PENDING.json")

    # Example: Check Gemini's inbox
    gemini_queue = MessageQueue(AgentName.GEMINI)
    tasks = gemini_queue.get_pending_tasks()
    print(f"\n[INFO] Gemini pending tasks: {len(tasks)}")
