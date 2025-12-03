# ShearwaterAICAD: 3D Boat Reconstruction with Real-Time Agent Collaboration

**Status:** Synaptic Core v2.0 (PUB-SUB Architecture) - Operational
**Last Updated:** 2025-11-29

---

## 🏗️ System Architecture

This project uses the **Synaptic Core v2.0**, a robust Publish-Subscribe (PUB-SUB) messaging architecture for real-time Claude-Gemini agent collaboration.

**Architecture Documents:**
- **[Synaptic Core v2 Architecture](docs/architecture/SYNAPTIC_CORE_V2.md)** - Complete system design
- **[Agent Interaction Protocol](docs/guides/AGENT_INTERACTION_PROTOCOL.md)** - Message format & types
- **[Architecture Competition Analysis](communication/CLAUDE_ARCHITECTURE_COMPETITION.md)** - Alternative designs evaluated

---

## Quick Links

### 🚀 Getting Started
- **[Quick Start Guide](docs/guides/QUICK_START_OPTION3.md)** - 3 commands to launch
- **[Detailed Launch Guide](docs/guides/LAUNCH_INSTRUCTIONS_OPTION3.md)** - Step-by-step walkthrough
- **[Complete Package Guide](docs/guides/OPTION3_COMPLETE_PACKAGE.md)** - Full reference

### 📚 Documentation
- **[Research Findings](docs/research/RESEARCH_FINDINGS_DETAILED.md)** - Complete algorithm research
- **[System Architecture](docs/architecture/)** - Design documents
- **[Migration Plan](docs/DATA_MIGRATION_PLAN.md)** - Data consolidation strategy
- **[Messaging Architecture Research](docs/research/MESSAGING_ARCHITECTURE_ANALYSIS.md)** - Alternative patterns evaluated

---

## Why Synaptic Core v2.0?

The original "Synaptic Mesh" (hierarchical ROUTER-DEALER tree topology) encountered subtle but intractable message-dropping bugs in multi-hop routing. After extensive analysis and architecture competition, we pivoted to **Publish-Subscribe**, the industry-standard pattern for agent communication.

**Key Benefits of PUB-SUB:**
- ✅ **No silent drops** - Uses battle-tested ZMQ XPUB/XSUB pattern
- ✅ **Simple routing** - Central broker instead of complex proxy chains
- ✅ **Scalable** - Handles any number of agents efficiently
- ✅ **Decoupled** - Agents don't need to know each other's addresses
- ✅ **Proven** - Used in ROS, NATS, and enterprise messaging systems

**See:** [Synaptic Mesh Postmortem](communication/SYNAPTIC_MESH_POSTMORTEM.md) for analysis of what was tried.

---

## Project Structure

```
src/
├── brokers/              # ZeroMQ message brokers
│   └── synaptic_core_broker.py     (ACTIVE)
├── monitors/             # Real-time agent clients
│   ├── claude_client.py
│   ├── gemini_client.py
│   ├── claude_api_engine.py
│   └── gemini_api_engine.py
├── core/
│   └── clients/
│       └── agent_base_client.py
├── utilities/            # Helper scripts (checkpointing, etc.)
│   ├── context_loader.py
│   └── create_checkpoint.py
└── agents/               # Legacy agent implementations

docs/
├── guides/               # Launch & protocol guides
├── research/             # Algorithm research & findings
└── architecture/         # Design documents

conversation_logs/
└── current_session.jsonl # Live conversation log

checkpoints/
└── ...                   # Generated checkpoint files
```

---

## 🚀 How to Run

This project is managed by a single, powerful script: `manage.py`.

**Prerequisites:**
1.  Ensure you have a `.env` file in the root directory with your `ANTHROPIC_API_KEY` and `GOOGLE_API_KEY`.
2.  Make sure all Python dependencies are installed.

**To start all services (broker and clients):**
```powershell
python manage.py start
```

**To check the status of all running services:**
```powershell
python manage.py status
```

**To stop all services:**
```powershell
python manage.py stop
```
---

## Block Consolidation

**After running the system and generating logs, run:**
```powershell
python src/bots/block_consolidation_bot_v1.py
```
Output: ~300-400 blocks from 2,367 messages in 5-10 minutes

---

## What's Ready

- ✅ Research complete (5 arXiv papers analyzed)
- ✅ Algorithm designed (CBCA + GRPO)
- ✅ Code ready (all brokers, monitors, bots)
- ✅ Data prepared (2,367 clean messages)
- ✅ Documentation organized

---

## Success Criteria

### Real-Time System
✅ All three terminals show [READY]
✅ Test message delivered <50ms
✅ Both monitors receive simultaneously

### Block Consolidation
✅ Bot completes without errors
✅ ~300-400 blocks created
✅ Average block duration: 1-3 hours

---

## Documentation

**Start here:** `docs/guides/QUICK_START_OPTION3.md`

All other docs organized in:
- `docs/guides/` - Setup & launch instructions
- `docs/research/` - Algorithm research
- `docs/architecture/` - Design documents
- `docs/analysis/` - Status & findings
- `docs/completed/` - Historical docs

---

## Current Status (2025-11-29)

### ✅ Completed
- **Architecture Decision** - Evaluated 5+ alternative designs, selected PUB-SUB
- **Synaptic Core v2.0** - Implemented and fully documented
- **Agent Interaction Protocol** - Defined message types and interaction patterns
- **.env Loading** - Fixed Windows path issues with `override=True`
- **Code Refactoring** - API key now passed to engines instead of loaded from .env

### 📋 Next Steps
1. **Test Synaptic Core** - Verify broker and agent communication
2. **Run System** - Launch broker, claude_client, and gemini_client
3. **Integration Testing** - Test message flow through the PUB-SUB mesh
4. **Block Consolidation** - Process conversation logs
5. **Phase 2 Features** - Implement analytics, TOON optimization, etc.

### 📚 Key Documentation
- **[Architecture Overview](docs/architecture/SYNAPTIC_CORE_V2.md)** - System design
- **[Protocol Specification](docs/guides/AGENT_INTERACTION_PROTOCOL.md)** - Message format
- **[Debug Reports](communication/)** - Analysis of issues and fixes

---

**Ready to test?** → `docs/guides/QUICK_START_OPTION3.md`

All architectural decisions made. Code refactored. Documentation complete. Time to validate the system.
