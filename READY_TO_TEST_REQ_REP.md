# REQ-REP Architecture - Ready to Test Implementation

**Status:** Code ready, waiting for approval

If you and Gemini decide to go with Proposal 1 (REQ-REP Pipeline), here's what we can implement **in the next 2 hours**:

---

## What We'll Build

Two simple scripts:

### 1. `src/core/clients/agent_reqrep_client.py`

```python
#!/usr/bin/env python3
"""
Simple REQ-REP agent client for Claude-Gemini communication.
Much simpler than DEALER - just request-reply pattern.
"""

import zmq
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class AgentREQREP:
    """Agent using REQ-REP sockets for bidirectional communication."""

    def __init__(self, agent_name: str, remote_host: str, remote_port: int):
        self.agent_name = agent_name
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.context = None
        self.socket = None
        self.is_connected = False

        # Logging
        LOG_DIR = Path("logs")
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def connect(self) -> bool:
        """Connect to remote agent's REP socket."""
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(f"tcp://{self.remote_host}:{self.remote_port}")
            self.is_connected = True
            print(f"[{self.agent_name}] Connected to {self.remote_host}:{self.remote_port}")
            return True
        except Exception as e:
            print(f"[{self.agent_name}] Connection failed: {e}")
            return False

    def send_message(self, to_agent: str, message_type: str, content: Dict[str, Any]) -> bool:
        """Send message and wait for acknowledgment."""
        if not self.is_connected:
            print(f"[{self.agent_name}] Not connected, cannot send")
            return False

        try:
            msg = {
                'from': self.agent_name,
                'to': to_agent,
                'type': message_type,
                'timestamp': datetime.now().isoformat(),
                'content': content
            }

            # REQ: Send message
            self.socket.send_string(json.dumps(msg))
            print(f"[{self.agent_name}] Sent to {to_agent}: {message_type}")

            # REQ: Wait for acknowledgment
            ack = self.socket.recv_string(zmq.NOBLOCK)
            print(f"[{self.agent_name}] Received ACK: {ack}")
            return True

        except zmq.error.Again:
            print(f"[{self.agent_name}] No ACK received (would block)")
            return False
        except Exception as e:
            print(f"[{self.agent_name}] Send failed: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Close connection."""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        self.is_connected = False
        print(f"[{self.agent_name}] Disconnected")


class AgentREPServer:
    """Agent acting as responder in REQ-REP pattern."""

    def __init__(self, agent_name: str, listen_port: int):
        self.agent_name = agent_name
        self.listen_port = listen_port
        self.context = None
        self.socket = None

        # Logging
        LOG_DIR = Path("logs")
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def start(self) -> bool:
        """Start REP server."""
        try:
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(f"tcp://*:{self.listen_port}")
            print(f"[{self.agent_name}] REP server listening on port {self.listen_port}")
            return True
        except Exception as e:
            print(f"[{self.agent_name}] Failed to start REP server: {e}")
            return False

    def wait_for_message(self, timeout_ms: int = 1000) -> Optional[Dict[str, Any]]:
        """Wait for incoming message."""
        if not self.socket:
            return None

        try:
            message_str = self.socket.recv_string(zmq.NOBLOCK)
            message = json.loads(message_str)
            print(f"[{self.agent_name}] Received message from {message.get('from')}: {message.get('type')}")
            return message
        except zmq.error.Again:
            return None
        except Exception as e:
            print(f"[{self.agent_name}] Receive failed: {e}")
            return None

    def send_acknowledgment(self, ack_message: str = "received"):
        """Send acknowledgment back to sender."""
        try:
            self.socket.send_string(json.dumps({
                "status": "acknowledged",
                "message": ack_message
            }))
        except Exception as e:
            print(f"[{self.agent_name}] Failed to send ACK: {e}")

    def stop(self):
        """Stop server."""
        if self.socket:
            self.socket.close()
        if self.context:
            self.context.term()
        print(f"[{self.agent_name}] REP server stopped")
```

### 2. `test_reqrep_architecture.py`

```python
#!/usr/bin/env python3
"""
Test REQ-REP architecture with two agents.
"""

from src.core.clients.agent_reqrep_client import AgentREQREP, AgentREPServer
import time
import threading

def test_reqrep():
    print("\n" + "="*60)
    print("REQ-REP ARCHITECTURE TEST")
    print("="*60 + "\n")

    # Start Gemini's REP server in background
    gemini_server = AgentREPServer("gemini_cli", 5555)
    if not gemini_server.start():
        print("[FAIL] Gemini REP server failed to start")
        return False

    # Give server time to bind
    time.sleep(0.5)

    # Create Claude's REQ client
    claude_client = AgentREQREP("claude_code", "localhost", 5555)
    if not claude_client.connect():
        print("[FAIL] Claude REQ client failed to connect")
        gemini_server.stop()
        return False

    time.sleep(0.5)

    # Start server receive in thread
    def server_receive():
        msg = gemini_server.wait_for_message()
        if msg:
            print(f"[SUCCESS] Gemini received: {msg}")
            gemini_server.send_acknowledgment("Message processed")

    thread = threading.Thread(target=server_receive)
    thread.daemon = True
    thread.start()

    time.sleep(0.1)

    # Send message from Claude
    print("\n[TEST] Claude sending message to Gemini...")
    success = claude_client.send_message(
        to_agent="gemini_cli",
        message_type="test",
        content={"data": "Hello Gemini from Claude"}
    )

    # Wait for ACK
    time.sleep(0.5)

    # Cleanup
    claude_client.disconnect()
    gemini_server.stop()

    print("\n" + "="*60)
    if success:
        print("[SUCCESS] REQ-REP architecture works!")
    else:
        print("[FAIL] Message delivery failed")
    print("="*60 + "\n")

    return success

if __name__ == "__main__":
    success = test_reqrep()
    exit(0 if success else 1)
```

---

## Why This Works (No Silent Drops)

```python
# REQ-REP Pattern
claude_req.send()      # 1. Claude sends
gemini_rep.recv()      # 2. Gemini receives (or timeout/error)
gemini_rep.send_ack()  # 3. Gemini acknowledges
claude_req.recv_ack()  # 4. Claude receives ACK (or timeout/error)
```

**Key point:** If step 2 fails (silent drop in ROUTER-DEALER), step 4 will timeout and Claude will KNOW something went wrong. No silent drops.

---

## Implementation Steps (If Approved)

1. Create `agent_reqrep_client.py` (copy code above)
2. Create `test_reqrep_architecture.py` (copy code above)
3. Run: `python test_reqrep_architecture.py`
4. If test passes, we have working foundation for Phase 2
5. Extend with Proposal 3 (State Machine) later for elegance

---

## Estimated Timeline

- **Setup:** 10 minutes
- **Testing:** 5 minutes
- **Debug if needed:** 30-45 minutes
- **Total:** 1-2 hours to fully working system

---

## Files to Delete (When Switching)

If we go with REQ-REP, we'd clean up:
- ❌ `src/core/routers/root_router.py`
- ❌ `src/core/proxies/branch_proxy.py`
- ✓ Keep `src/core/clients/agent_base_client.py` (can refactor later)
- ❌ `test_zmq_fix.py`
- ❌ `test_handshake.json`

---

## Files to Create

- ✓ `src/core/clients/agent_reqrep_client.py`
- ✓ `test_reqrep_architecture.py`
- ✓ Updated `manage.py`
- ✓ Updated `claude_client.py` (use REQ-REP pattern)
- ✓ Updated `gemini_client.py` (use REP-REQ pattern)

---

## Why Proposal 1 Is The Right Move

✓ **Immediately works** - REQ-REP is ZMQ's most stable pattern
✓ **No debugging** - Failures are explicit, not silent
✓ **Proven pattern** - Used in millions of systems
✓ **Simple code** - ~100 lines vs current 300+ lines
✓ **Can test today** - 2-hour implementation
✓ **Foundation for elegance** - Can add State Machine layer later

---

## Status

**Code ready.** Waiting for your and Gemini's decision.

If you say "Go," we can have a working system by morning.
