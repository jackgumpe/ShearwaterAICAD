# Synaptic Mesh: Implementation Guide (Token-Oriented Object Notation)

**Audience**: Claude Code (Lead Implementer)
**Author**: Gemini (Architect)
**Purpose**: To provide a concise, token-efficient specification of the Synaptic Mesh backend components.

---

### **File 1: `root_router.py`**

```
// FILE: src/core/routers/root_router.py

OBJECT: RootRouter (conceptual)
  DESCRIPTION: "The central hub for inter-branch communication. Listens for messages from all branch proxies and forwards them to the correct destination branch."
  
  PROPERTIES:
    - context: zmq.Context -> The global ZeroMQ context.
    - router_socket: zmq.Socket:ROUTER -> Listens for incoming messages from branch proxies.
    - message_log: collections.deque -> In-memory log for the last 10,000 messages for persistence and replay.
  
  METHODS:
    - main():
        INPUT: None
        ACTION: 
          1. Initializes ZMQ context and ROUTER socket.
          2. Binds ROUTER socket to the root port (e.g., 5550).
          3. Enters an infinite loop to receive and forward messages.
          4. Receives multipart messages in the format: [sender_identity, destination_identity, json_payload].
          5. Logs the payload to the `message_log`.
          6. Forwards the message to the destination using the format: [destination_identity, sender_identity, json_payload].
        RETURNS: None (blocking loop)
```

---

### **File 2: `branch_proxy.py`**

```
// FILE: src/core/proxies/branch_proxy.py

OBJECT: BranchProxy (conceptual)
  DESCRIPTION: "A local hub for agents within a specific domain or 'branch'. It handles intra-branch communication and forwards inter-branch messages to the Root Router."

  PROPERTIES:
    - context: zmq.Context -> The global ZeroMQ context.
    - agent_router: zmq.Socket:ROUTER -> Listens for messages from agents within its branch.
    - root_dealer: zmq.Socket:DEALER -> Connects to the Root Router for inter-branch communication.
    - poller: zmq.Poller -> Manages non-blocking reads from both sockets.

  METHODS:
    - main(branch_name, branch_port, root_router_address):
        INPUT: 
          - branch_name (str): The name of this branch.
          - branch_port (int): The port for this proxy to listen on.
          - root_router_address (str): The full address of the Root Router.
        ACTION:
          1. Initializes ZMQ context, ROUTER socket, and DEALER socket.
          2. Binds the `agent_router` to the specified `branch_port`.
          3. Connects the `root_dealer` to the `root_router_address`.
          4. Enters an infinite loop using a `poller` to handle incoming messages from both sockets.
          5. **If message from agent (via `agent_router`):** Forwards it to the Root Router via `root_dealer`.
          6. **If message from Root Router (via `root_dealer`):** Forwards it to the correct agent via `agent_router`.
        RETURNS: None (blocking loop)
```

---

This documentation provides the essential structure and logic for the backend components. With these in place, we are now ready to connect the refactored agent clients (`gemini_client.py`, `claude_client.py`) and perform our first end-to-end test.
