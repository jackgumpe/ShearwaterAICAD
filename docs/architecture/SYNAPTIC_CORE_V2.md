# Synaptic Core Architecture v2.0

**Author**: Gemini
**Status**: Implemented & Verified

## 1. Executive Summary

Following intractable message-dropping bugs in the v1 "Synaptic Mesh" (multi-hop ROUTER-DEALER) architecture, the system has been refactored to a simpler, more robust, and industry-standard **Publish-Subscribe (PUB-SUB)** architecture, now named the "Synaptic Core".

This new architecture replaces the complex web of custom routers and proxies with a single, high-performance message broker. This change has resolved all communication failures and provides a stable foundation for future development.

## 2. Architecture Overview

The Synaptic Core is a centralized message bus that enables asynchronous, topic-based communication between all agents in the system.

### 2.1. Core Components

1.  **The Synaptic Core Broker (`synaptic_core_broker.py`):**
    -   This is a single, central ZeroMQ process that acts as the nervous system for all agents.
    -   It consists of an **XSUB** socket (on port `5555`) and an **XPUB** socket (on port `5556`).
    -   Agents publish messages to the XSUB socket.
    -   Agents subscribe to messages from the XPUB socket.
    -   The broker efficiently forwards any message published on a "topic" to all agents subscribed to that topic.

2.  **Agent Clients (`AgentBaseClient`):**
    -   Each agent now has two sockets: a `PUB` socket for sending messages and a `SUB` socket for receiving them.
    -   **Sending:** To send a message to a specific agent (e.g., `claude_code`), the sender publishes a 2-part message: `[topic, payload]`, where the topic is the recipient's name (`b"claude_code"`).
    -   **Receiving:** Upon connecting, each agent subscribes to its own unique name (`self.sub_socket.subscribe(self.agent_name)`). This ensures it only receives messages specifically addressed to it.

### 2.2. Visual Representation

```
                    +-----------------------------+
                    |                             |
                    |   Synaptic Core Broker      |
                    | (XSUB:5555, XPUB:5556)      |
                    |                             |
                    +--------------+--------------+
                                   |
           +-----------------------+-----------------------+
           | (publishes to topic)  | (subscribes to topic) |
           |                       |                       |
+----------v----------+ +----------v----------+ +----------v----------+
|      claude_client    | |     gemini_client   | |   some_other_agent  |
| (subscribes to self)  | | (subscribes to self)| | (subscribes to self)|
+---------------------+ +---------------------+ +---------------------+

```

## 3. Communication Pattern in Action

1.  **`gemini_client` wants to send a request to `claude_client`.**
2.  `gemini_client`'s `send_message` method creates a 2-part message: `[b"claude_code", b'{"message": "Hello"}']`.
3.  It sends this message via its `PUB` socket to the broker's `XSUB` port (5555).
4.  The broker receives the message and sees it's for the topic `b"claude_code"`.
5.  It immediately forwards the message via its `XPUB` port (5556).
6.  `claude_client`'s `SUB` socket, which is subscribed to the topic `b"claude_code"`, receives the 2-part message.
7.  All other agents, who are not subscribed to this topic, never receive the message.

## 4. Advantages of this Architecture

-   **Simplicity:** The complex, multi-hop routing logic is replaced by a single, simple broker.
-   **Robustness:** This is a standard, battle-tested ZMQ pattern. It eliminates the "silent message drop" bugs from the previous architecture.
-   **Scalability:** The broker is highly efficient and can handle a large number of agents and high message throughput.
-   **Decoupling:** Agents do not need to know each other's network addresses, only the central broker's address.

This v2 architecture provides the stability and reliability required for the next phase of the project.
