# Agent Message Publishing Implementation Guide

**Status:** BLUEPRINT READY
**Priority:** CRITICAL - Required to fully utilize persistent recording system
**Date:** 2025-11-30

---

## The Problem

The persistent recording broker is deployed and working, but agents aren't publishing messages to it. Result:

- ✅ Broker can record messages
- ✅ Recording infrastructure is in place
- ❌ Agents don't send messages to broker
- ❌ Conversations aren't captured

**Evidence:** Latest log entry from Nov 20, but it's now Nov 30. No new messages recorded despite active agent conversations.

---

## Why This Matters

Without agent message publishing:
- No automatic conversation history
- Can't analyze agent collaboration patterns
- No recovery of lost conversations
- No ACE tier/chain type metadata on actual conversations
- Metadata enrichment system sits unused

---

## Three Implementation Options

### Option A: Message Hook Integration (RECOMMENDED)

**Where:** Modify agent message handling to publish after processing

**File:** `src/monitors/claude_client.py` (same for gemini_client.py)

**Implementation:**
```python
import zmq
import json
from datetime import datetime

class AgentWithPublishing:
    def __init__(self):
        # ... existing init ...

        # Add PUB socket for publishing to broker
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.connect("tcp://localhost:5555")

    def process_incoming_message(self, message):
        """Hook called when message received"""
        # Process the message normally
        result = self._handle_message(message)

        # Publish to broker for recording
        self._publish_to_broker({
            'event_type': 'message_processed',
            'agent': self.agent_name,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': message.get('message_id'),
            'sender': message.get('from'),
            'content': message.get('content'),
            'result': result
        })

        return result

    def _publish_to_broker(self, event):
        """Publish event to broker for recording"""
        try:
            topic = f"{self.agent_name}_events".encode()
            payload = json.dumps(event).encode('utf-8')
            self.pub_socket.send_multipart([topic, payload])
            print(f"[PUBLISH] Event published to broker: {event['event_type']}")
        except Exception as e:
            print(f"[ERROR] Failed to publish: {e}")
```

**Advantages:**
- ✅ Non-invasive - just adds publish calls
- ✅ Captures actual messages being processed
- ✅ Preserves full context (sender, receiver, result)
- ✅ Works with existing agent code

**Where to add:** In `src/monitors/claude_client.py` after line where messages are processed

---

### Option B: Periodic Status Publishing

**Where:** Agent main loop publishes status every N seconds

**Implementation:**
```python
import threading
import zmq
import json
from datetime import datetime

class AgentWithPeriodicPublishing:
    def __init__(self):
        # ... existing init ...
        self.pub_socket = zmq.Context().socket(zmq.PUB)
        self.pub_socket.connect("tcp://localhost:5555")

        # Start periodic publisher thread
        self.publish_thread = threading.Thread(target=self._publish_periodic, daemon=True)
        self.publish_thread.start()

    def _publish_periodic(self):
        """Publish status every 30 seconds"""
        import time
        while True:
            try:
                status = {
                    'event_type': 'status_update',
                    'agent': self.agent_name,
                    'timestamp': datetime.utcnow().isoformat(),
                    'state': 'active',
                    'messages_processed': self.message_count,
                    'uptime_seconds': time.time() - self.start_time
                }

                topic = f"{self.agent_name}_status".encode()
                payload = json.dumps(status).encode('utf-8')
                self.pub_socket.send_multipart([topic, payload])

                time.sleep(30)  # Publish every 30 seconds
            except Exception as e:
                print(f"[ERROR] Status publish failed: {e}")
```

**Advantages:**
- ✅ Lightweight - just status updates
- ✅ Continuous proof of agent life
- ✅ Minimal overhead
- ✅ Good for monitoring agent health

**Disadvantages:**
- ❌ Doesn't capture actual conversation content
- ❌ Less detailed metadata

---

### Option C: Explicit Event Publishing

**Where:** Agent publishes specific events (decisions, errors, completions)

**Implementation:**
```python
class AgentWithEventPublishing:
    def __init__(self):
        # ... init ...
        self.pub_socket = zmq.Context().socket(zmq.PUB)
        self.pub_socket.connect("tcp://localhost:5555")

    def publish_event(self, event_type, content):
        """Publish a specific event"""
        event = {
            'event_type': event_type,
            'agent': self.agent_name,
            'timestamp': datetime.utcnow().isoformat(),
            'content': content
        }

        topic = f"{self.agent_name}_events".encode()
        payload = json.dumps(event).encode('utf-8')
        self.pub_socket.send_multipart([topic, payload])
        print(f"[PUBLISH] {event_type}: {content}")

    def on_message_received(self, message):
        self.publish_event('message_received', message)

    def on_decision_made(self, decision):
        self.publish_event('decision_made', decision)

    def on_error(self, error):
        self.publish_event('error_occurred', error)

    def on_completion(self, result):
        self.publish_event('task_completed', result)
```

**Advantages:**
- ✅ Explicit control over what's published
- ✅ Rich metadata per event type
- ✅ Easy to add new event types
- ✅ Perfect for debugging

**Disadvantages:**
- ❌ Requires identifying all event points
- ❌ More code changes required

---

## Recommended Path Forward

### Phase 1: Quick Integration (30 minutes)
Implement **Option A** - message hook publishing:
1. Add PUB socket to `AgentBaseClient` or individual agent classes
2. Call publish in existing message handling code
3. Test with simple conversation between agents
4. Verify messages appear in `conversation_logs/current_session.jsonl`

### Phase 2: Comprehensive Integration (2-3 hours)
Add **Option C** - explicit event publishing:
1. Identify all critical decision points in agent code
2. Add `publish_event()` calls at those points
3. Create event type schema
4. Test with full agent conversation
5. Verify metadata enrichment works

### Phase 3: Monitoring (1 hour)
Add **Option B** - periodic status:
1. Add status publishing thread
2. Monitor agent health via published events
3. Set up alerts for agent failures
4. Create dashboard from published metrics

---

## Testing the Implementation

After implementing message publishing:

```bash
# 1. Start services
python manage.py start

# 2. Let agents communicate for a minute

# 3. Check if new messages were recorded
tail -20 conversation_logs/current_session.jsonl | python -m json.tool

# 4. Verify metadata
python -c "
import json
with open('conversation_logs/current_session.jsonl') as f:
    for line in f.readlines()[-5:]:
        msg = json.loads(line)
        print(f'{msg.get(\"Timestamp\")}: {msg.get(\"SpeakerName\")} - Chain:{msg.get(\"Metadata\", {}).get(\"chain_type\")}, Tier:{msg.get(\"Metadata\", {}).get(\"ace_tier\")}')
"

# 5. Verify recovery
python manage.py stop
sleep 1
python manage.py start
# Check if [RECOVERY] message appears in logs
```

---

## Message Publishing Checklist

Before implementation:
- [ ] Understand current agent message handling flow
- [ ] Identify where to add pub_socket initialization
- [ ] Choose which option to implement (A, B, or C)
- [ ] Plan minimal code changes
- [ ] Create test cases

During implementation:
- [ ] Add PUB socket connection code
- [ ] Add publish calls in message handling
- [ ] Test with single message first
- [ ] Verify message appears in log file
- [ ] Check metadata enrichment

After implementation:
- [ ] Full conversation test (agent-to-agent communication)
- [ ] Crash recovery test (stop/restart broker)
- [ ] Log analysis (verify all event types captured)
- [ ] Performance check (no slowdown)
- [ ] Documentation update

---

## Code Snippets to Copy

### PUB Socket Initialization
```python
import zmq

# In agent __init__
self.pub_socket = zmq.Context().socket(zmq.PUB)
self.pub_socket.connect("tcp://localhost:5555")
print(f"[PUBLISHING] Connected to broker at tcp://localhost:5555")
```

### Simple Publish Function
```python
def _publish_to_broker(self, message_dict):
    """Publish message to broker"""
    try:
        topic = self.agent_name.encode()
        payload = json.dumps(message_dict).encode('utf-8')
        self.pub_socket.send_multipart([topic, payload])
    except Exception as e:
        print(f"[ERROR] Publish failed: {e}")
```

### Integration Point
```python
# After processing a message, publish it
def on_message_received(self, message):
    # Process message
    result = self.handle_message(message)

    # Publish to broker for recording
    self._publish_to_broker({
        'event': 'message_processed',
        'original_message': message,
        'processing_result': result
    })

    return result
```

---

## Success Criteria

After implementation, these should be true:

✅ `conversation_logs/current_session.jsonl` file grows with new timestamps
✅ Broker shows `[LOG #]` messages in output
✅ Messages have ACE tier classification
✅ Messages have chain type detection
✅ Messages have SHL tags
✅ Broker gracefully recovers after restart
✅ No slowdown in agent operation

---

## Notes

- Broker listens on `tcp://localhost:5555` (FRONTEND_PORT)
- All messages must be [topic, payload] multipart format
- Topic should be bytes (e.g., b"agent_name")
- Payload should be JSON-encoded bytes
- Uses ZeroMQ XPUB/XSUB internally (transparent to agents)

---

## Next Steps

1. **Choose implementation option** (A recommended)
2. **Modify appropriate agent file** (claude_client.py or gemini_client.py)
3. **Test with simple conversation**
4. **Verify messages in log file**
5. **Deploy to both agents**
6. **Monitor and iterate**

The persistent recording system is ready. It just needs agents to use it.
