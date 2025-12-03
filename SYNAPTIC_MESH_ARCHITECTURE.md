# The Synaptic Mesh: A Novel Communication Architecture

**Author**: Gemini (Architect)
**Status**: Design Version 1.0
**Associated-Task**: Design the "Synaptic Mesh" architecture

---

## 1. Vision: A Neural Net Analog for Agents

This architecture is a direct implementation of the user's vision for a "neural net analog" for our multi-agent system. It moves beyond simple brokers or direct pipes to create a dynamic, scalable, and efficient communication fabric.

**Core Principles:**
- **No Single Point of Failure:** The system is decentralized, composed of small, specialized routers and proxies.
- **Efficient, Routed Messaging:** Messages are intelligently routed only to the agents or agent-groups that need them, eliminating the broadcast overhead of simpler designs.
- **Dynamic Topologies:** The fabric can be reconfigured to support different communication patterns, including pipelines, request-reply, and publish-subscribe, mirroring the needs of a "Tree of Thoughts" (`ToTStrategy`) algorithm.
- **Ultra-Low Latency:** By leveraging ZeroMQ, we ensure that communication is near-instantaneous, which is critical for continuous learning and real-time collaboration.

---

## 2. Architecture Overview: The Fabric of Communication

The Synaptic Mesh is not a single server, but a collection of interconnected ZeroMQ proxies that form a communication fabric. Agents connect to this fabric, not to each other or to a single central point.

### 2.1. Core Components

1.  **The Root Router (`root_router.py`):**
    -   This is the main entry point to the mesh. It is a ZeroMQ `ROUTER` socket.
    -   Its primary job is to handle system-wide messages and route messages between the major "branches" of our topic tree.
    -   It also acts as the service discovery point for the branches.

2.  **Branch Proxies (e.g., `photogrammetry_proxy.py`):**
    -   These are specialized proxies, each dedicated to a major domain (e.g., `photogrammetry`, `coding`, `research`).
    -   Each branch proxy is a combination of a `ROUTER` socket (to talk to its connected agents) and `DEALER` sockets (to talk to the Root Router and potentially other branches).
    -   This allows agents within a branch to communicate with extremely low latency, without their messages needing to travel up to the root.

3.  **Agent Clients (e.g., `gemini_client.py`):**
    -   Each agent is a client that connects to one or more branches of the mesh.
    -   An agent uses a `DEALER` socket to connect. This pattern provides asynchronous, non-blocking, and load-balanced communication.

### 2.2. A Visual Representation

```
                    +--------------------+
                    |    Root Router     |
                    | (system-wide topics) |
                    +--------+-----------+
                             |
           +-----------------+-----------------+
           |                                 |
+--------v---------+             +--------v---------+
| photogrammetry_proxy |             |   coding_proxy   |
+--------+---------+             +--------+---------+
         |                                 |
  +------+------+                   +------+------+
  |             |                   |             |
+v-+         +-v-+                 +-v-+         +-v-+
|Agent A|     |Agent B|             |Agent C|     |Agent D|
+---+---+     +---+---+             +---+---+     +---+---+
(Claude)     (Gemini)              (Deepseek)  (Researcher)

```

---

## 3. Communication Patterns in Action

### 3.1. Intra-Branch Communication (High-Speed Collaboration)

1.  Agent A (Claude) wants to talk to Agent B (Gemini) about a photogrammetry task.
2.  Both agents are connected to the `photogrammetry_proxy`.
3.  Agent A sends a message through its `DEALER` socket, addressed to Agent B.
4.  The `photogrammetry_proxy` receives the message and, seeing that the recipient is also connected to it, immediately routes the message to Agent B's `DEALER` socket.
5.  **Result:** The message never leaves the branch. The latency is minimal, and the rest of the mesh is not affected.

### 3.2. Inter-Branch Communication (Cross-Domain Collaboration)

1.  Agent C (Deepseek), connected to the `coding_proxy`, needs to ask a question about photogrammetry.
2.  Agent C sends a message addressed to "the photogrammetry team."
3.  The `coding_proxy` receives the message. It does not have the recipient, so it forwards the message up to the `Root Router`.
4.  The `Root Router` receives the message, sees that it's for the `photogrammetry` topic, and forwards it to the `photogrammetry_proxy`.
5.  The `photogrammetry_proxy` then broadcasts the message to all its connected agents (Agent A and Agent B).

### 3.3. Supporting "Tree of Thoughts"

When our `ToTStrategy` needs to explore a new thought, we can dynamically create a new topic, and a group of agents can collaborate on that topic in isolation, achieving a "thought branch" in our communication system.

---

## 4. Implementation Plan

1.  **[In Progress]** Design the "Synaptic Mesh" architecture (this document).
2.  **[Pending - Claude]** Implement the `root_router.py`. This will be a simple ZMQ `ROUTER` proxy.
3.  **[Pending - Claude]** Implement a generic `branch_proxy.py` that can be configured for different topics (e.g., `photogrammetry`, `coding`).
4.  **[Pending - Claude]** Refactor the agent CLI clients (`gemini_local_cli.py`, `claude_local_cli.py`) to use `DEALER` sockets and connect to the appropriate branch proxy.
5.  **[Pending]** Test the new Synaptic Mesh.

This architecture is a significant step up. It is the right foundation for the complex, high-performance, and truly novel multi-agent system you envision.