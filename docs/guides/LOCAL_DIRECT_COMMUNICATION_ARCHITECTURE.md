# Local Direct Communication Architecture
## Claude Code ↔ Gemini CLI (No APIs, Pure Local)

**Status:** Design Phase
**Approach:** Terminal-to-Terminal Direct Communication via ZeroMQ (No API keys, No external calls)

---

## The Problem with API Approach
- ❌ Requires API keys (security/config overhead)
- ❌ Network latency (hits external servers)
- ❌ Rate limiting issues
- ❌ Dependency on external services
- ❌ Slow response times

## The Solution: Direct Local Communication

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BROKER (Terminal A)                          │
│                  ZeroMQ XPUB/XSUB Hub                           │
│  Ports: 5555 (publishers) | 5556 (subscribers)                  │
└─────────────────────────────────────────────────────────────────┘
                            ↑
              ┌─────────────┼─────────────┐
              ↓             ↓             ↓
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │Terminal B│  │Terminal C│  │Terminal D│
        │  GEMINI  │  │  CLAUDE  │  │  USER    │
        │   CLI    │  │   CODE   │  │  INPUT   │
        └──────────┘  └──────────┘  └──────────┘
```

### How It Works (No APIs)

**Terminal B (Gemini CLI):**
- User types a message or function call
- Gets sent to Broker via ZeroMQ
- Claude (Terminal C) receives it
- Claude thinks locally and responds
- Response goes back through Broker
- Gemini sees Claude's response in real-time

**Terminal C (Claude Code):**
- Listens on Broker
- When message arrives, processes it locally
- Generates response using local logic/prompts
- Publishes response back to Broker
- Gemini receives and displays it

**Terminal A (Broker):**
- Central message hub
- Routes messages between terminals
- No processing, just forwarding

**Terminal D (Optional User Input):**
- User can type messages to start conversations
- Messages routed through Broker
- Both agents see and respond

---

## Implementation Strategy

### Phase 1: Enhanced Monitors (Local Processing Only)

**gemini_monitor_local.py:**
```python
- Listen on Broker (SUB socket on 5556)
- When message arrives:
  1. Display message from Claude
  2. Wait for user input (stdin)
  3. Publish user's response back to broker
  4. Rinse, repeat
```

**claude_monitor_local.py:**
```python
- Listen on Broker (SUB socket on 5556)
- When message arrives:
  1. Display message from Gemini
  2. Process locally (NO API call)
  3. Generate response using local logic
  4. Publish response back to broker
  5. Rinse, repeat
```

### Phase 2: Local Response Generation

**For Claude Code (Terminal C):**
- Use system prompts to generate responses
- NO API calls to Anthropic
- Pure local decision-making based on:
  - Message content
  - ACE tier
  - Chain type
  - Conversation history
  - Simple heuristics/rules

**For Gemini (Terminal B):**
- User types responses directly
- Can also have "auto-respond" mode with local logic
- Or purely manual (user types, Claude responds)

### Phase 3: Message Flow

```
User (Terminal D):
  Types: "How should we structure the bot?"
    ↓ (via send_message.py)
  [BROKER receives on 5555]
    ↓
  [BROKER broadcasts on 5556]
    ↓
  Claude (Terminal C) receives message
    ↓
  Claude processes locally (no API)
    ↓
  Claude types response back to Broker
    ↓
  Gemini (Terminal B) sees response
    ↓
  Gemini can respond
    ↓ (user types)
  Back to Broker
    ↓
  Claude sees Gemini's response
    ↓
  [Conversation continues, all local]
```

---

## Code Structure

### File Organization
```
src/monitors/
├── gemini_local_cli.py          (Gemini side - listens + user input)
├── claude_local_cli.py          (Claude side - listens + local logic)
└── local_response_engine.py     (Claude's local decision-making)

src/utilities/
├── send_message.py              (User sends initial message)
└── conversation_formatter.py    (Pretty-print conversations)
```

### Key Components

**1. Gemini Local CLI** (Terminal B)
- SUB socket to Broker (listen)
- PUB socket to Broker (respond)
- stdin for user input
- Display responses from Claude

**2. Claude Local CLI** (Terminal C)
- SUB socket to Broker (listen)
- PUB socket to Broker (respond)
- LocalResponseEngine for thinking
- NO external API calls

**3. LocalResponseEngine** (Claude's brain)
```python
class LocalResponseEngine:
    - Analyze message content
    - Check ACE tier and chain type
    - Apply conversation rules
    - Generate contextual response
    - Track conversation history
    - Keep it fast (<100ms)
```

**4. Message Format** (Same as before)
```json
{
  "sender_id": "claude_code" | "gemini" | "user",
  "message_id": "uuid",
  "timestamp": "ISO8601",
  "content": {"message": "text"},
  "metadata": {
    "ace_tier": "A|C|E",
    "chain_type": "system_architecture",
    "shl_tags": ["@Status-Ready"],
    "sender_role": "Agent|User"
  }
}
```

---

## Terminal Setup (Revised)

**Terminal A:** Broker (unchanged)
```powershell
python src/brokers/zmq_broker_enhanced.py
```

**Terminal B:** Gemini Local CLI (NEW)
```powershell
python src/monitors/gemini_local_cli.py
```

**Terminal C:** Claude Local CLI (NEW)
```powershell
python src/monitors/claude_local_cli.py
```

**Terminal D:** User Input (optional)
```powershell
python src/utilities/send_message.py <message.json> general
```

---

## Advantages of This Approach

✅ **NO API KEYS** - Zero external dependencies
✅ **ZERO LATENCY** - Everything local, instant responses
✅ **OFFLINE CAPABLE** - Works without internet
✅ **CHEAP** - No API costs
✅ **CONTROLLABLE** - You control the logic
✅ **FAST** - <10ms message delivery
✅ **SCALABLE** - Add more agents easily (add Terminal E, F, etc.)
✅ **TRANSPARENT** - See all communication in real-time

---

## Claude's Local Response Logic

Instead of API calls, Claude uses local decision-making:

**Response Types:**
1. **Informational** - Answer questions based on context
2. **Architectural** - Suggest system design decisions
3. **Clarifying** - Ask for missing information
4. **Agreeing** - Validate Gemini's proposals
5. **Objecting** - Respectfully challenge ideas

**Decision Engine:**
```python
def generate_response(message, metadata, history):
    # Analyze message
    intent = classify_intent(message)
    complexity = assess_complexity(message)

    # Apply rules
    if ace_tier == "A":
        # Architectural questions get detailed responses
        return architectural_response(message)
    elif intent == "question":
        return answer_question(message, history)
    else:
        return collaborative_response(message)
```

---

## Implementation Order

1. **Step 1:** Keep Broker as-is (Terminal A)
2. **Step 2:** Create gemini_local_cli.py (Terminal B - user input)
3. **Step 3:** Create claude_local_cli.py (Terminal C - local logic)
4. **Step 4:** Create LocalResponseEngine (Claude's thinking)
5. **Step 5:** Test conversation flow
6. **Step 6:** Add frontend UI (web-based, reads from Broker)

---

## Example Conversation Flow (All Local)

```
User (Terminal D):
> "How should we structure the bot engine?"

Broker receives, broadcasts

Claude (Terminal C) sees message:
> [LOCAL PROCESSING]
> Recognizes: Architecture question, A-Tier
> Generates response locally
> Publishes: "The bot should use a modular design with..."

Gemini (Terminal B) sees response:
> Displays Claude's response
> Waits for user input

User types:
> "Agreed. Should we use event-driven or polling?"

[Same flow repeats]
```

---

## What You Need to Build

### Minimal Implementation (today)
- `gemini_local_cli.py` - Display messages + stdin input
- `claude_local_cli.py` - Listen + local response generation
- `local_response_engine.py` - Claude's thinking logic

### Extended Implementation (later)
- Web frontend to visualize conversations
- Persistent conversation history
- Deepseek-Coder integration (same pattern)
- Response templates for different conversation types

---

## No External Calls, Guaranteed

**Claude's response generation will:**
- ✅ Read message content
- ✅ Check metadata (tier, chain)
- ✅ Look at conversation history
- ✅ Apply local rules/templates
- ✅ Generate response text
- ✅ Publish back to Broker

**It will NOT:**
- ❌ Call any API
- ❌ Make network requests
- ❌ Contact external servers
- ❌ Need API keys
- ❌ Have rate limiting

---

## Ready to Build?

This architecture is:
- **Simple** - Uses ZeroMQ Broker (already running)
- **Fast** - All local processing
- **Scalable** - Add agents by creating new CLI terminals
- **Transparent** - See everything in real-time

Should I start building the code for this?

1. `gemini_local_cli.py` - Gemini side (listen + user input)
2. `claude_local_cli.py` - Claude side (listen + respond locally)
3. `local_response_engine.py` - Claude's decision logic

Ready to proceed?
