# Agent Interaction Protocol v1.0

This document defines the standard message types and interaction patterns for agents communicating within the ShearwaterAICAD system via the Synaptic Core (PUB-SUB) broker.

## Message Structure

All messages published to the broker are 2-part ZeroMQ messages: `[topic, payload]`.

- **Topic:** The `topic` is a UTF-8 encoded string that corresponds to the recipient's `agent_name` (e.g., `b"claude_code"`).
- **Payload:** The `payload` is a UTF-8 encoded JSON string with the following structure:

```json
{
    "message_id": "string (unique identifier)",
    "timestamp": "string (ISO 8601 format)",
    "from": "string (sender's agent_name)",
    "to": "string (recipient's agent_name)",
    "type": "string (one of the defined protocol types)",
    "priority": "string (e.g., 'NORMAL', 'HIGH', 'LOW')",
    "content": {
        "message": "string (the primary text content/question)",
        "...": "any other relevant data"
    }
}
```

## Protocol Message Types

The `type` field in the payload determines how the recipient agent should process the message.

### 1. `request`

- **Purpose:** Used when the sender requires a direct answer or a confirmation of a task from the recipient. This is the primary message type for initiating a two-way conversation.
- **Sender's Action:** Publishes a message with `type: "request"`.
- **Recipient's Action:** Upon receiving a `"request"`, the agent's `process_incoming_message` method should:
    1. Parse the `content`.
    2. Perform the necessary action (e.g., call its API engine to generate an answer).
    3. Publish a new message of `type: "response"` back to the original sender.

### 2. `response`

- **Purpose:** Used to reply to a `"request"` message.
- **Sender's Action:** An agent will only send a `"response"` after processing a `"request"`.
- **Recipient's Action:** Upon receiving a `"response"`, the agent's `process_incoming_message` method should:
    1. Log that the response was received.
    2. **NOT** generate a new response, to prevent infinite loops.
    3. The content can be stored or used to update the agent's internal state.

### 3. `inform`

- **Purpose:** A one-way message used to provide information or log an event without expecting a direct reply. This is useful for status updates or broadcasting information to a central logging agent.
- **Sender's Action:** Publishes a message with `type: "inform"`.
-   **Recipient's Action:** Upon receiving an `"inform"` message, the agent's `process_incoming_message` method should:
    1. Log the information.
    2. **NOT** generate a response.

---

By adhering to this protocol, we can create complex, purposeful, and non-looping conversations between our autonomous agents.
