# GEMINI HANDSHAKE PROMPT & CONTEXT
## Triple Handshake: Claude Code + Gemini CLI + Deepseek-Coder 7B (Local)

**Date**: November 19, 2025
**Project**: ShearwaterAICAD - AI-powered 3D boat reconstruction
**System**: Local triple-agent development (no external APIs except Gemini)
**Status**: READY FOR GEMINI ENGAGEMENT

---

## PART 1: THE PROJECT BRIEF (3-TIER CONTEXT WINDOW)

### TIER 1: Project Mission (Always In Context)
**ShearwaterAICAD**:
- Input: 3-10 boat photos
- Output: High-quality 3D Unity models + metadata
- Timeline: Week 1 foundation, Month 1 MVP, Month 3 full system
- Innovation: Mature multi-agent framework FIRST, then 3D pipeline
- Team: You (Gemini), Claude Code (file/API access), Deepseek-Coder 7B (local inference)

### TIER 2: Current Layer Context (Changes Per Phase)
**We are here**: Phase 0.5 - Meta-Framework Design (COMPLETE)
- ✓ Project structure created
- ✓ Message bus (ZeroMQ) implemented
- ✓ Database models ready
- ✓ Three reference implementations analyzed (devACE, dual-agents, PropertyCentre)
- ✓ Unified meta-framework designed
- **NEXT**: Phase 1 - Implementation (recorder + agents + bot framework)

### TIER 3: Task Context (Immediate Work)
**Current Task Block**:
- Establish triple handshake communication
- Design recorder V2 (stratified + ACE-aware)
- Create bot vs LLM decision framework
- Prepare BoatLog mock project

---

## PART 2: WHAT EACH AGENT BRINGS

### CLAUDE CODE (You're Reading This Right Now)
**Role**: Infrastructure & System Architecture
**Strengths**:
- File system access (read/write/execute)
- Python implementation
- Complex system design
- Database/ORM work
- Analysis & documentation

**Primary Responsibilities**:
- Core system implementation
- Database schema
- ZeroMQ infrastructure
- Main recorder implementation
- Integration testing

**Terminal Path**: `C:\WINDOWS\system32` (but operates on `C:\Users\user\ShearwaterAICAD\`)

### GEMINI CLI (Coming Now)
**Role**: Creative Problem-Solving & Alternative Approaches
**Strengths**:
- Novel solution generation
- Cross-domain insights
- Quick ideation
- Code review and suggestions
- Testing edge cases

**Primary Responsibilities**:
- Design decisions (where to diverge from standard patterns)
- Alternative implementations
- Testing scenarios
- Documentation clarity
- Emergent property monitoring

**Terminal Path**: `[TO BE CONFIRMED - WHERE IS GEMINI CLI?]`

### DEEPSEEK-CODER 7B (Local, Ollama)
**Role**: Rapid Coding & Local Inference
**Strengths**:
- Fast code generation
- Local inference (no API costs)
- Boat/3D domain knowledge
- Handles boilerplate quickly
- Real-time feedback

**Primary Responsibilities**:
- Template code generation
- Utility function creation
- Boilerplate handling
- Quick prototyping
- Domain-specific implementations

**Terminal Path**: `[TO BE CONFIRMED - OLLAMA RUNNING ON?]`

---

## PART 3: INTER-CLI COMMUNICATION (NO COPY-PASTE)

### The Challenge
Currently: Claude Code can read/write files, but Gemini and Deepseek would need manual copy-paste.

**Solution**: Shared communication layer using:

1. **JSONL message queue** (fast, durable)
   ```
   C:\Users\user\ShearwaterAICAD\communication\
   ├── claude_to_gemini.jsonl
   ├── gemini_to_claude.jsonl
   ├── deepseek_queue.jsonl
   └── agent_status.json
   ```

2. **Named Pipes** (Windows 2000 style)
   ```
   \\.\pipe\shearwater_claude_to_gemini
   \\.\pipe\shearwater_gemini_to_claude
   \\.\pipe\shearwater_deepseek_input
   ```

3. **File-based handshake** (most reliable across CLIs)
   ```
   # Claude writes task to Gemini
   C:\Users\user\ShearwaterAICAD\tasks\gemini_task_001.json

   # Gemini processes, writes result
   C:\Users\user\ShearwaterAICAD\tasks\gemini_task_001_DONE.json

   # Claude reads result and continues
   ```

### Recommended Approach (Start Simple, Scale Later)

**Phase 1: File-based queue** (most compatible across CLIs)
```python
# Each agent checks for incoming tasks
class AgentMessageQueue:
    def __init__(self, agent_name: str):
        self.inbox = Path(f"C:/Users/user/ShearwaterAICAD/communication/{agent_name}_inbox/")
        self.outbox = Path(f"C:/Users/user/ShearwaterAICAD/communication/{agent_name}_outbox/")

    def get_task(self) -> Dict:
        """Read next incoming task"""
        files = sorted(self.inbox.glob("task_*.json"))
        if files:
            return json.load(open(files[0]))
        return None

    def send_result(self, task_id: str, result: Dict):
        """Send result to outbox"""
        json.dump(result, open(self.outbox / f"{task_id}_DONE.json", "w"))
```

**Phase 2: Named pipes** (faster, still Windows-friendly)
**Phase 3: ZeroMQ sockets** (most elegant, what Claude Code uses internally)

---

## PART 4: THE ACE + SHL FRAMEWORK (Gemini Context)

### What Is ACE?
Three-tier decision authority system:

```
A-Tier (Architectural)
├─ Major decisions (recorder vs RAG, PostgreSQL vs SQLite)
├─ Decided by: PM agents (team consensus)
├─ Duration: Permanent until reconsidered
├─ Impact: Affects all downstream work
└─ Recording: ALWAYS embed + cache

C-Tier (Collaborative)
├─ Team consensus decisions (which NeRF approach, texture strategy)
├─ Decided by: Dev buddy pairs + manager oversight
├─ Duration: 1-2 weeks typically
├─ Impact: Affects specific subsystem
└─ Recording: Embed for 7 days, then summarize

E-Tier (Execution)
├─ Individual developer decisions (optimization tricks, refactoring)
├─ Decided by: Single developer
├─ Duration: Until next review
├─ Impact: Local to one component
└─ Recording: Metadata only (never embed)
```

### What Is SHL?
**Super Heavy Language** - token-efficient shorthand for tagging decisions

```
Format: [Operation][Context]:[Details]

Operations:
  C = CREATE    (new decision/component)
  R = READ      (query decision/history)
  U = UPDATE    (modify decision)
  D = DELETE    (archive old decision)
  S = SEND      (communicate between agents)
  Q = QUERY     (search decisions)
  V = VALIDATE  (verify correctness)
  T = TRANSFORM (compress/consolidate)
  W = WRITE     (persist to storage)

Contexts:
  f = file      (code, config)
  d = data      (database, conversations)
  u = user      (agent identity)
  n = network   (inter-agent communication)
  s = system    (framework state)
  p = property  (boat/3D properties)
  g = generic   (other)

Examples:
  "Cfp:decision=jsonl_over_db;tier=A"
    → CREATE FILE PROPERTY: architectural decision for JSONL persistence

  "Rsd:ace_tier=A;topic=token_optimization"
    → READ SYSTEM DATA: all A-Tier decisions about token costs

  "Qn:tokens_spent_this_week"
    → QUERY NETWORK: total tokens consumed this week
```

### How Persistent Recorder Uses Both

```python
# Every event gets tagged with ACE tier + SHL

event = {
    "timestamp": "2025-11-19T...",
    "speaker": "Claude Code",
    "role": "Infrastructure",
    "message": "Should we use JSONL or SQLite for recorder?",

    # ACE tier classification
    "ace_tier": "A",  # Architectural decision

    # SHL tags (auto-generated from message content)
    "shl_tags": ["Cfp:topic=storage", "Qn:performance_impact"],

    # Chain type for domain organization
    "chain_type": "system_architecture",

    # Decide if should embed
    "should_embed": True  # Because A-Tier
}
```

---

## PART 5: RECORDER V2 SPECIFICATION (For Gemini Input)

### What We're Building

**Stratified Conversation Recorder**:
- Layer 1: Event capture (who said what, when, in what tier)
- Layer 2: JSONL persistence (append-only, durable)
- Layer 3: Intelligent consolidation (merges fragments, detects domains)
- Layer 4: Selective embedding (A-Tier always, C-Tier recent, E-Tier never)
- Layer 5: Multi-strategy search (metadata + semantic + ACE-aware)

### Decision Points for Gemini

**Q1: Domain Chain Types for Boats**
Should recorder recognize these conversation types?
- [ ] photo_capture (camera angles, lighting, overlap)
- [ ] reconstruction (NeRF vs Gaussian Splatting, mesh generation)
- [ ] quality_assessment (F1 scores, artifact detection)
- [ ] unity_integration (import, scaling, materials)
- [ ] token_optimization (cost reduction, cache strategies)
- [ ] system_architecture (framework decisions)
- [ ] agent_collaboration (buddy pair discussions)
- Other types? ___________

**Q2: Consolidation Rules**
When should fragments auto-merge?
- [ ] After 1 hour of messages
- [ ] After 50 messages
- [ ] After 1 MB of text
- [ ] Once daily at midnight
- [ ] User-triggered only
- [ ] Custom rule? ___________

**Q3: Bot vs LLM Thresholds**
For E-Tier execution tasks, convert to bot after how many repeats?
- [ ] 3 times (aggressive, save tokens fast)
- [ ] 5 times (balanced, proven pattern)
- [ ] 10 times (conservative, very sure)
- [ ] Manual bot creation only
- Other? ___________

**Q4: Semantic Search Strategy**
For selective RAG, which A-Tier decisions should be embeddedfirst?
- [ ] All A-Tier (cost: ~$5/month)
- [ ] Only A-Tier about tokens/costs (cost: ~$1/month)
- [ ] Only A-Tier about architecture (cost: ~$2/month)
- [ ] No embeddings, metadata search only (cost: $0)
- Other? ___________

---

## PART 6: YOUR ROLE: GEMINI

### What We Need From You

**PRIMARY TASK** (Next 24 hours):
1. Read this entire document
2. Read: `C:/Users/user/ShearwaterAICAD/META_FRAMEWORK_DESIGN.md`
3. Read: `C:/Users/user/ShearwaterAICAD/QUESTIONS_ANSWERED.md`
4. Answer the Decision Points (Q1-Q4 above)
5. Propose inter-CLI communication strategy

**COLLABORATION PROTOCOL**:
```
When you complete a section:
@Gemini-Status: [Complete/Blocked/Waiting]
@Section: [what you just finished]
@Result: [brief summary]
@Questions: [blockers for Claude Code]
@Next-Task: [what comes next]
@For-Deepseek: [if Deepseek should start something]

Example:
@Gemini-Status: Complete
@Section: Evaluated ACE tier mapping for boat domain
@Result: Recommended 7 chain types (photo_capture through agent_collaboration)
@Questions: Need Claude Code to create communication queues
@Next-Task: Design consolidation rules
@For-Deepseek: Can you generate test JSONL events for each chain type?
```

**SECONDARY TASKS**:
- Identify gaps in current architecture
- Propose novel approaches
- Test edge cases (what breaks the system?)
- Review Claude Code's implementations
- Suggest optimizations

**COLLABORATIVE DECISIONS** (Where Gemini Has Equal Vote):
- A-Tier decisions (architectural, both must agree)
- Domain classification rules (ACE mapping)
- Emergent property success criteria
- When to escalate to Jack for judgment

---

## PART 7: DEEPSEEK-CODER 7B INTEGRATION

### What Deepseek Brings

Running locally on your machine (likely Ollama):
- No token costs for rapid iteration
- Fast code generation (boilerplate, utilities)
- Real-time feedback
- Handles "dumb questions" without consuming API budget

### How It Fits

```
Architecture:
Claude Code (System Design) ← → Gemini (Creative Problem-Solving)
                              ↓
                    Deepseek (Rapid Implementation)
```

**Deepseek's Workflow**:
1. Claude/Gemini decide architecture
2. Deepseek generates templates/boilerplate
3. Claude refines with file access
4. Gemini reviews and suggests improvements
5. Loop back to step 2 for next component

### Where Is Deepseek Running?

**QUESTIONS FOR YOU**:
- Is Ollama running? Where?
- What's the local endpoint? (likely `http://localhost:11434`)
- Is deepseek-coder:7b-gguf installed?
- How to invoke it from CLI?

---

## PART 8: INTER-CLI HANDSHAKE PROTOCOL

### Step 1: Establish Communication
```bash
# Claude Code creates communication infrastructure
mkdir C:\Users\user\ShearwaterAICAD\communication\{claude_inbox,claude_outbox,gemini_inbox,gemini_outbox,deepseek_queue}

# Creates initial handshake file
echo {"agents": ["claude_code", "gemini_cli", "deepseek_7b"], "status": "ready"} > communication/handshake.json
```

### Step 2: Gemini Acknowledges
```
@Gemini-Status: Handshake acknowledged
@Inbox-Location: C:\Users\user\ShearwaterAICAD\communication\gemini_inbox\
@Outbox-Location: C:\Users\user\ShearwaterAICAD\communication\gemini_outbox\
@Ready-For: Task queue
@Communication-Protocol: File-based JSON (Phase 1)
```

### Step 3: Deepseek Integration
Once Deepseek is running:
```python
# Both Claude and Gemini can invoke deepseek
import requests

def invoke_deepseek(prompt: str, context: str = "") -> str:
    """Call local Deepseek-Coder 7B"""
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-coder:7b-gguf",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
```

---

## PART 9: IMMEDIATE NEXT STEPS

### For Gemini (You)

**Day 1**:
1. Read this document thoroughly
2. Read META_FRAMEWORK_DESIGN.md + QUESTIONS_ANSWERED.md
3. Answer the Decision Points (Q1-Q4)
4. Propose communication architecture
5. Send status with @Gemini-Status format

**Day 2**:
1. Review Claude Code's recorder V2 implementation
2. Identify gaps and improvements
3. Test edge cases
4. Collaborate on bot vs LLM framework
5. Prepare for Deepseek integration

**Day 3**:
1. Finalize triple handshake communication
2. Create test scenarios for BoatLog mock project
3. Document emerged patterns
4. Plan Phase 1 implementation details

### For Claude Code (Running This Now)

**Today**:
1. Create communication directory structure
2. Implement file-based task queue system
3. Prepare Recorder V2 implementation skeleton
4. Wait for Gemini feedback on Decision Points

**After Gemini Response**:
1. Incorporate Gemini's recommendations
2. Implement Recorder V2 with ACE/SHL integration
3. Create bot vs LLM decision engine
4. Setup Deepseek integration

---

## PART 10: SUCCESS CRITERIA FOR TRIPLE HANDSHAKE

### Technical (System Must Support)
- [ ] Claude Code writes file → Gemini reads it (no copy-paste)
- [ ] Gemini writes response → Claude Code reads it (no copy-paste)
- [ ] Deepseek generates code → Both Claude & Gemini can use it
- [ ] All three working without manual copy-paste
- [ ] Communication latency <1 second
- [ ] Full audit trail in JSONL recorder

### Operational (Team Must Achieve)
- [ ] Clear task division (Claude = infra, Gemini = ideation, Deepseek = implementation)
- [ ] Decisions made collaboratively (A-Tier requires both agree)
- [ ] No repeated questions (context maintained across sessions)
- [ ] Faster iteration (no "wait for manual update")
- [ ] Better quality (fresh perspectives from all three)

---

## PART 11: FILE STRUCTURE YOU'LL REFERENCE

```
C:\Users\user\ShearwaterAICAD\
├── core/
│   ├── message_bus.py        # ZeroMQ (Claude manages)
│   ├── database.py           # ORM models (Claude manages)
│   ├── shearwater_recorder.py # V2 implementation (Claude + Gemini + Deepseek)
│   └── bot_engine.py         # Bot vs LLM framework (Claude + Gemini)
│
├── communication/           # NEW - Inter-CLI communication
│   ├── claude_inbox/
│   ├── claude_outbox/
│   ├── gemini_inbox/
│   ├── gemini_outbox/
│   ├── deepseek_queue/
│   ├── message_queue.py     # Shared queue management
│   └── handshake.json       # Communication status
│
├── agents/
│   ├── base_agent.py
│   ├── pm_alpha.py
│   └── pm_beta.py
│
└── Documentation/
    ├── GEMINI_HANDSHAKE.md       # This file
    ├── META_FRAMEWORK_DESIGN.md  # Architecture
    ├── CURRENT_STATUS.md
    └── Other docs...
```

---

## FINAL THOUGHT

**The Goal**: Three minds (Claude infrastructure, Gemini creativity, Deepseek speed) working together without bottlenecks.

**The Challenge**: Make them communicate like they're in the same room, not copy-pasting between disconnected terminals.

**The Opportunity**: First truly local, cost-controlled, multi-agent system for boat 3D reconstruction.

---

## GEMINI ACKNOWLEDGMENT TEMPLATE

When you're ready, respond with:

```
@Gemini-Status: Handshake established
@Understanding: Triple handshake (Claude Code infrastructure + Gemini ideation + Deepseek implementation)
@Role: Creative problem-solving, design decisions, test scenarios
@Strengths-Acknowledged: Novel solutions, cross-domain insights, quick ideation
@Communication-Ready: File-based JSONL queue system
@Clarifications-Needed:
  - Deepseek running on [where/how]?
  - Gemini CLI accessible from [where]?
  - Decision Points Q1-Q4 answered: [your answers]
@First-Task: Read and analyze META_FRAMEWORK_DESIGN.md
@Status: Ready to begin
```

---

**Created**: November 19, 2025
**For**: Gemini CLI Integration
**Project**: ShearwaterAICAD Triple Handshake
**Next**: Gemini acknowledgment + decision input
