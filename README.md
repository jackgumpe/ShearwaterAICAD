# ShearwaterAICAD

**AI-powered 3D boat reconstruction using a double-agent system (Codex + Claude Code)**

## Quick Start

### 1. Setup Environment
```bash
cd C:\Users\user\ShearwaterAICAD
source venv/Scripts/activate  # Windows
# or
. venv/Scripts/activate  # Windows PowerShell
```

### 2. Configure API Keys
Edit `.env`:
```env
KIMI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./shearwater_aicad.db
```

### 3. Run Tests
```bash
python tests/test_triple_handshake.py
```

## Project Structure

- **agents/** - Agent implementations
  - `base_agent.py` - Abstract base class
  - `pm_alpha.py` - PM-Alpha (The Architect)
  - `pm_beta.py` - PM-Beta (The Executor)
  - `dev_agents.py` - Dev-1 through Dev-4 (TODO)

- **core/** - Core system components
  - `message_bus.py` - ZeroMQ pub/sub communication
  - `database.py` - SQLAlchemy ORM models
  - `conversation_recorder.py` - Conversation logging (TODO)

- **conversations/** - JSONL conversation streams
  - `_streams/` - Organized by context_id

- **tests/** - Test suite
  - `test_triple_handshake.py` - Agent collaboration test

## Key Documents

### For Everyone
- **PHASE_0_COMPLETE.md** - Foundation setup status and next steps
- **README.md** (this file) - Quick reference

### For Codex
- **CODEX_HANDSHAKE.md** - Your complete instructions and protocol
- **CONVERSATION_RECORDER_ANALYSIS.md** - Decision on recorder vs RAG

### For Claude Code
- **ShearwaterAICAD brief.txt** (in project root) - Full project vision

## System Architecture

### Double Handshake
```
Codex Terminal ↔ Claude Code
     ↓                  ↓
  PM-Beta          Base Framework
     ↓                  ↓
  Dev Agents      Message Bus
     ↓                  ↓
ZeroMQ Pub/Sub    SQLite DB
```

### Agent Personalities
- **PM-Alpha** (Claude): The Architect - Strategic, thorough, documentation-heavy
- **PM-Beta** (OpenAI): The Executor - Pragmatic, fast, ship-focused
- **Dev-1** (Kimi): The Optimist - Always sees positive side
- **Dev-2** (Claude): The Skeptic - Devil's advocate
- **Dev-3** (Codex): The Pragmatist - "Good enough" mindset
- **Dev-4** (Kimi): The Perfectionist - Wants perfect code

## Communication Protocol

Between Codex and Claude Code:

```
@Codex-Status: Ready/Blocked/Waiting/Complete
@Implementation: [code or description]
@Location: [file path]
@NextStep: [what comes next]
@Questions: [blockers]
@Notes: [personality observations]
```

## Database Models

```python
Conversation  # Each agent utterance
  - Id (UUID)
  - Timestamp
  - SpeakerName (agent name)
  - SpeakerRole (Manager/Developer)
  - Message (content)
  - ConversationType (enum)
  - ContextId (session grouping)
  - Metadata (dict)

Decision  # High-level decisions (A-Tier)
CodeCommit  # Code changes
Reflection  # Agent self-analysis
PerformanceMetric  # Metrics tracking
```

## Workflow

### Phase 0: Foundation ✓ COMPLETE
- Project setup
- Core infrastructure
- Agent framework
- Analysis documents

### Phase 1: Mock Project (TODO)
- **Project**: BoatLog web app
- **Goal**: Test agent collaboration
- **Duration**: ~6 hours
- **Tools**: Agents debate, design, implement, review

### Phase 2: 3D Research (TODO)
- Few-Shot NeRF research
- Boat photo capture patterns
- Initial prototype

### Phase 3: Reflection (TODO)
- Agent self-analysis
- Day 2 planning

## Key Files to Know

### Must Read (In Order)
1. `PHASE_0_COMPLETE.md` - Overview of what's done
2. `CODEX_HANDSHAKE.md` - If you're Codex
3. `CONVERSATION_RECORDER_ANALYSIS.md` - Decision rationale
4. `agents/base_agent.py` - How agents work
5. `core/message_bus.py` - How communication works

### Reference
- `core/database.py` - Database schema
- `.env.example` - Configuration template
- `tests/test_triple_handshake.py` - Working example

## Running the System

### Interactive Mode (Coming Soon)
```bash
# Start message bus listener
python -m core.message_bus &

# Start agents
python -m agents.pm_alpha &
python -m agents.pm_beta &

# Start dev agents
python -m agents.dev_agents &
```

### Test Mode (Now)
```bash
python tests/test_triple_handshake.py
```

### Reflection/Analysis
```bash
python -c "from core.database import init_db; db = init_db(); print(db.query(Conversation).count())"
```

## Next Steps

1. **Codex**: Read `CODEX_HANDSHAKE.md`
2. **Codex**: Verify directory access, enter standby
3. **Claude Code**: Implement Dev agents
4. **Claude Code**: Create conversation recorder
5. **Both**: Run Phase 1 (BoatLog project)
6. **Both**: Reflect and iterate

## Questions?

- System architecture → `PHASE_0_COMPLETE.md`
- Conversation approach → `CONVERSATION_RECORDER_ANALYSIS.md`
- Agent implementation → `agents/base_agent.py`
- Communication protocol → `CODEX_HANDSHAKE.md`

## Status

**Phase**: 0 (Foundation) - COMPLETE ✓
**Ready**: YES
**Next**: Codex engagement + Dev agent implementation
**Timeline**: Week 1 foundation, Month 1 MVP, Month 3 full system

---

**Created**: November 2025
**Double Handshake**: Codex + Claude Code
**Next Milestone**: Phase 1 BoatLog Completion
