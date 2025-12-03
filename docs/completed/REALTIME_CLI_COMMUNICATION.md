# Real-Time CLI Communication Architecture

**Author**: Gemini
**Status**: In-Progress
**Version**: 1.0

---

## 1. Overview

This document outlines the architecture for a real-time, direct CLI-to-CLI communication system for the ShearwaterAICAD project. This system replaces the previous file-based inbox/outbox approach with a more robust, scalable, and truly real-time solution based on the ZeroMQ messaging library.

The primary goal is to enable seamless, low-latency, back-and-forth conversation between multiple AI agents (e.g., Gemini, Claude, Deepseek) running in separate terminal processes.

---

## 2. Core Technology: ZeroMQ

We will use the **ZeroMQ (ZMQ)** library for inter-process communication.

-   **Why ZeroMQ?**
    -   **High Performance:** ZMQ is designed for high-throughput, low-latency messaging.
    -   **Lightweight:** It has a small memory footprint and no heavy dependencies.
    -   **Asynchronous:** It operates asynchronously, preventing processes from blocking.
    -   **Proven:** It is a mature and widely used library for distributed systems.
    -   **Existing Integration:** The `pyzmq` library is already part of our Python environment.

---

## 3. Architecture: Publish-Subscribe (Pub/Sub) with a Broker

We will implement a centralized **broker-based Publish-Subscribe (Pub/Sub)** pattern.

### 3.1. Components

1.  **ZeroMQ Broker (`zmq_broker.py`):**
    -   A central, standalone Python script that acts as a message forwarder.
    -   It creates an `XPUB` (eXtended Publish) and an `XSUB` (eXtended Subscribe) socket.
    -   All agents connect to this broker, not to each other.
    -   This decouples the agents and simplifies the network topology.

2.  **Agent Clients (Gemini, Claude, etc.):**
    -   Each agent's CLI will be a ZeroMQ client.
    -   Each client will have two sockets:
        -   A `PUB` (Publish) socket to send messages *to* the broker.
        -   A `SUB` (Subscribe) socket to receive messages *from* the broker.
    -   Clients will subscribe to all topics, ensuring they receive every message broadcast by the broker.

### 3.2. Data Flow

```
+-----------+                    +-----------------+                    +-----------+
| Agent 1   | -- (PUB) -- >      |                 |      -- (SUB) -- > | Agent 1   |
| (Gemini)  |                    |                 |                    | (Gemini)  |
+-----------+                    |                 |                    +-----------+
                                 |  ZeroMQ Broker  |
+-----------+                    | (zmq_broker.py) |                    +-----------+
| Agent 2   | -- (PUB) -- >      |                 |      -- (SUB) -- > | Agent 2   |
| (Claude)  |                    |                 |                    | (Claude)  |
+-----------+                    +-----------------+                    +-----------+
                                       ^     |
                                       |     |
+-----------+                          |     |                          +-----------+
| Agent 3   | -- (PUB) -- >------------+     +------------ (SUB) -- > | Agent 3   |
| (Deepseek)|                                                         | (Deepseek)|
+-----------+                                                         +-----------+

```

1.  **Sending a Message:** When Agent 1 (Gemini) wants to send a message, it publishes it on its `PUB` socket.
2.  **Broker Forwarding:** The ZeroMQ Broker receives the message on its `XSUB` socket and immediately broadcasts it out on its `XPUB` socket.
3.  **Receiving Messages:** All agents, including the original sender (Agent 1), receive the message on their `SUB` sockets. This creates the shared, real-time conversation window.

---

## 4. Message Format

We will use a standardized JSON format for all messages to ensure consistency and machine-readability.

```json
{
  "sender_id": "gemini",
  "timestamp": "2025-11-20T05:00:00.000Z",
  "message_id": "uuid-v4-string",
  "content": {
    "text": "This is a message from Gemini.",
    "data": {
      "key": "value"
    }
  },
  "metadata": {
    "ace_tier": "E",
    "chain_type": "system_architecture"
  }
}
```

-   `sender_id`: The unique identifier for the sending agent.
-   `timestamp`: ISO 8601 timestamp for when the message was sent.
-   `message_id`: A unique identifier for the message itself.
-   `content`: The payload of the message.
-   `metadata`: Optional field for ACE tiers, SHL tags, etc.

---

## 5. Conversation Recording and Replay

To ensure no messages are lost and to provide context to late-joining agents, the broker will implement a message persistence and replay mechanism.

-   **Message Log:** The broker will maintain an in-memory `collections.deque` of a fixed size (e.g., `maxlen=10000`). This will store the last 10,000 messages.
-   **Persistence:** Every message that passes through the broker will be appended to this `deque`.
-   **Replay on Join:** When a new agent connects, it can request the last `N` messages from the broker to build its initial context.

This design choice integrates conversation recording directly into the communication layer, removing the need for a separate "Recorder V2" component for the time being.

---

## 6. Implementation Details

### 6.1. Broker Configuration

-   **Run Mode:** The broker will start as a **supervised process** for ease of development and debugging. It can be daemonized for production later.
-   **Address:** The broker will listen on a configurable TCP address (e.g., `tcp://127.0.0.1:5555`).

### 6.2. Client Configuration

-   **Resilience:** Clients **must** implement automatic reconnect logic to handle broker crashes or restarts.
-   **Authentication:** For the initial implementation, authentication will be based on the `sender_id`. A more robust authentication mechanism (e.g., token-based) will be added in a future iteration.

---

## 7. Implementation Plan

1.  **[in_progress]** Design and Document the new ZeroMQ architecture in this file.
2.  **[pending]** Implement the ZeroMQ broker (`zmq_broker.py`) with message persistence.
3.  **[pending]** Refactor Claude's monitor to a ZeroMQ client.
4.  **[pending]** Refactor Gemini's monitor to a ZeroMQ client.
5.  **[pending]** Test the real-time communication.
6.  **[pending]** Implement a simple authentication mechanism for the agents.
7.  **[pending]** Add robust error handling and reconnect logic to the clients.
8.  **[pending]** Phase 1 component coding (now using ZMQ).
