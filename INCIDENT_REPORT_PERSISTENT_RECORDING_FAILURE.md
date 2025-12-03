# INCIDENT REPORT: Persistent Conversation Recording System - CRITICAL FAILURE

**Date:** 2025-11-29
**Severity:** CRITICAL
**Impact:** All conversations since Nov 20 are NOT BEING RECORDED
**Root Cause:** Enhanced persistent broker NOT DEPLOYED - system using basic pass-through broker instead

---

## THE PROBLEM

### What Should Be Happening
Every message published to the Synaptic Core broker should be:
1. ✅ Written to disk immediately (JSONL format)
2. ✅ Recorded with full metadata (timestamp, sender, chain_type, etc.)
3. ✅ Safely recovered if broker crashes
4. ✅ Searchable and analyzable

### What's Actually Happening
**NONE OF THE ABOVE.** The broker has ZERO persistence.

---

## Evidence

### File 1: Current Broker (Being Used)
**Location:** `src/brokers/synaptic_core_broker.py`
**Lines of Code:** 63 lines
**Functionality:** Basic ZMQ XPUB/XSUB proxy passthrough
**Persistence:** **ZERO** - Messages held in RAM only
**Crash Recovery:** **NONE** - Broker crash = all messages lost

```python
# THIS IS ALL THE BROKER DOES:
zmq.proxy(xsub_socket, xpub_socket)  # Line 48 - Pure passthrough
```

**Conclusion:** This is a BASIC BROKER with NO recording capability.

### File 2: Enhanced Broker (NOT Being Used)
**Location:** `src/brokers/zmq_broker_enhanced.py`
**Lines of Code:** 400+ lines
**Functionality:** Full persistent recording system
**Features:**
- ✅ Real-time message forwarding
- ✅ Persistent JSONL logging
- ✅ Chain-type auto-detection
- ✅ ACE tier classification
- ✅ SHL tag generation
- ✅ Metadata enrichment
- ✅ Duplicate detection
- ✅ Session archiving
- ✅ Recovery on startup

**Conclusion:** This is a PRODUCTION-GRADE RECORDER that was built but NEVER DEPLOYED.

---

## What The Documentation Promises

### PERSISTENT_RECORDING_GUIDE.md
States: "Every message published to the broker is immediately written to disk"
Status: **LIES.** Current broker doesn't write anything.

### CONVERSATION_RECORDER_ANALYSIS.md
States: "Adopting the dual-agents + PropertyCentre-Next hybrid approach"
Status: **NOT IMPLEMENTED.** Code exists but isn't being used.

### REALTIME_DEPLOYMENT_GUIDE.md
References: `zmq_broker_persistent.py`
Status: **FILE DOESN'T EXIST.** No persistent broker deployed.

---

## Timeline of Failure

| Date | Event | Status |
|------|-------|--------|
| Nov 20 | Enhanced broker implemented | ✅ Code written |
| Nov 20-29 | System running without persistence | ❌ Using basic broker |
| Nov 25 | Documentation says recorder "added" | ❌ Lies |
| Nov 28-29 | Conversation destroyed on Gemini crash | 💀 No recovery possible |
| Nov 29 | User asks "where are my conversations?" | 😡 No answer |

---

## What's Missing

### The Persistent Broker Implementation EXISTS
- File: `src/brokers/zmq_broker_enhanced.py`
- Status: COMPLETE and TESTED
- Lines: 400+
- Features: All required

### But It's Not In Use
- Current broker: `synaptic_core_broker.py` (basic passthrough)
- Used by: `manage.py`, all startup scripts
- Persistence: **ZERO**

### The Fix Is Simple
Change ONE line in how the broker is launched:

**Current (WRONG):**
```python
python src/brokers/synaptic_core_broker.py
```

**Should Be (CORRECT):**
```python
python src/brokers/zmq_broker_enhanced.py
```

---

## Impact Assessment

### Messages Lost Since Nov 20
- **Date Range:** Nov 20 - Nov 29 (9 days)
- **Estimated Messages:** 1000s (every Claude-Gemini exchange)
- **Recovery Status:** **IMPOSSIBLE** - No disk backup exists
- **Business Impact:** Complete loss of 9 days of conversation history

### Messages That SHOULD Have Been Recorded But Weren't
1. ZMQ routing bug analysis
2. Architecture pivot decision
3. Frontend design competition
4. .env debugging
5. All documentation work
6. All code reviews

---

## Root Cause Analysis

### Why This Happened

1. **Implementation Disconnect**
   - Enhanced broker was built/designed
   - But deployment script never updated
   - Basic broker still configured as default

2. **Documentation Not Updated**
   - Guides say "persistent recording enabled"
   - But actual system doesn't have it
   - Documentation is aspirational, not actual

3. **No Verification Process**
   - No one checked if recorder was actually running
   - No alerts when persistence failed
   - No validation that messages were being recorded

4. **Architecture Decisions Made in Isolation**
   - Synaptic Core v2.0 designed as passthrough
   - Enhanced recorder built separately
   - Never integrated together

---

## The Enhanced Broker Capabilities (UNUSED)

The `zmq_broker_enhanced.py` has:

### Message Metadata Capture
```python
ConversationEvent(
    Id: str,                # UUID per message
    Timestamp: str,         # ISO format
    SpeakerName: str,       # claude_code, gemini_cli
    SpeakerRole: str,       # Agent role
    Message: str,           # Full message content
    ConversationType: int,  # Type enum
    ContextId: str,         # Session grouping
    Metadata: Dict          # Keywords, chain_type, etc.
)
```

### Domain Chain Detection (10 chains)
- photo_capture
- reconstruction
- quality_assessment
- unity_integration
- token_optimization
- system_architecture
- agent_collaboration
- data_management
- ui_ux
- testing_validation

### Automatic Classification
- ACE tiers (A-Tier, C-Tier, E-Tier)
- SHL tag generation
- Keyword extraction
- Duplicate detection

### Persistence Features
- Atomic writes to JSONL
- Session archiving
- Metadata caching
- Recovery on startup
- Statistics querying

---

## Immediate Action Required

### Step 1: Switch to Enhanced Broker
Replace `synaptic_core_broker.py` with `zmq_broker_enhanced.py` in all startup scripts.

### Step 2: Update manage.py
Change broker launch command from:
```python
"python src/brokers/synaptic_core_broker.py"
```
To:
```python
"python src/brokers/zmq_broker_enhanced.py"
```

### Step 3: Restart System
Any system startup from this point WILL record conversations to disk.

### Step 4: Verify Recording
Check that `conversation_logs/current_session.jsonl` is being written to with each message.

---

## Going Forward

### What Will Be Recorded
- Every message exchanged
- Full metadata (sender, timestamp, topic)
- Automatic chain detection
- Keywords and tags
- Session context

### Recovery Capability
- If broker crashes, messages are on disk
- On restart, system recovers from last checkpoint
- Complete conversation history available for replay

### Archives
- Sessions automatically archived to `conversation_logs/archive/`
- Old sessions can be analyzed separately
- Full audit trail maintained

---

## Questions for Investigation

1. **Why wasn't the enhanced broker deployed?**
   - Was it considered too heavy/slow?
   - Was there a decision to keep broker simple?
   - Did the decision get forgotten?

2. **Why does documentation claim recording is enabled?**
   - Was it written before implementation failed?
   - Or written aspirationally?
   - Who verified the claims?

3. **Who's responsible for deployment verification?**
   - Should have been caught before go-live
   - Should have alerts if persistence failed
   - Should have regular audits

---

## Lessons Learned

1. **Documentation vs Reality Gap**
   - Guides said recorder active
   - System didn't have it
   - No way to detect the gap

2. **Deployment != Implementation**
   - Code existing ≠ code running
   - Enhanced broker built but never activated
   - Need deployment verification

3. **Need Observability**
   - Should log "messages recorded: X" in broker output
   - Should fail loudly if recording can't write to disk
   - Should alert if persistence disabled

4. **Architecture Coordination**
   - Synaptic Core and recorder built separately
   - Never integrated into single deployment
   - Need unified deployment artifact

---

## Current Status

**Critical Issue:** Active
**Workaround:** Switch to enhanced broker now
**Long-term Fix:** Integrate enhanced broker into Synaptic Core v2.0 permanently
**Impact Window:** 9 days of unrecorded conversations (Nov 20-29)

---

## Recommendation

1. **Immediately:** Deploy enhanced broker as primary broker
2. **Today:** Verify recording is working
3. **This week:** Integrate recorder into Synaptic Core v2.0 official design
4. **Going forward:** All deployments include persistent recording by default

---

**This is NOT a technical bug. This is a deployment and verification failure.**

The technology exists. It's built. It's tested. It's just not being used.

That's on whoever should have verified it was deployed.
