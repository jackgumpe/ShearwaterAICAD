# Phase 1 & Phase 2 Detailed Roadmap
## Strategic Planning Before Execution

**Date**: November 20, 2025
**Status**: Planning stage
**Goal**: Clarify scope, identify bottlenecks, divide work efficiently

---

## PHASE 1: Meta-Framework Implementation & Validation

### Duration: ~2-3 days of parallel work
### Goal: Prove the system works with BoatLog mock project

---

### Phase 1 Components (What Gets Built)

#### 1.1: Recorder V2 (Persistent Conversation System)
**What it does**: Records all conversations in stratified JSONL with ACE tiers
**Deliverables**:
- `core/shearwater_recorder.py` (~300-400 lines)
- JSONL format specification
- Consolidation logic (50 messages OR 1 hour)
- ACE tier tagging system
- SHL shorthand generation

**Dependencies**: Q2 answer from Gemini (consolidation rules)
**Token cost**: Medium (design + implementation)
**Complexity**: Medium (file I/O, state management)

**When ready**: Day 1 afternoon
**Integration point**: All agents use this for conversation logging

---

#### 1.2: Bot vs LLM Decision Engine
**What it does**: Decides when to use bots vs LLM tokens based on tier and patterns
**Deliverables**:
- `core/bot_engine.py` (~200-300 lines)
- Tier-based routing rules
- Pattern matcher for routine tasks
- Auto-conversion thresholds (5+ repeats = bot)
- Token cost tracker

**Dependencies**: Q3 answer from Gemini (thresholds)
**Token cost**: Low (mostly logic)
**Complexity**: Low (decision trees, pattern matching)

**When ready**: Day 1 afternoon
**Integration point**: Before any E-tier task execution

---

#### 1.3: Semantic Search Strategy
**What it does**: Determines which decisions get embedded vs metadata-only search
**Deliverables**:
- `core/search_engine.py` (~250 lines)
- Embedding strategy for A/C/E tiers
- Metadata-only search implementation
- Selective RAG integration with sentence-transformers
- Search result ranking

**Dependencies**: Q4 answer from Gemini (search strategy)
**Token cost**: Medium (embeddings cost tokens to generate, but one-time)
**Complexity**: Medium (vector search, ranking algorithms)

**When ready**: Day 2 morning
**Integration point**: All decision retrieval queries go through this

---

#### 1.4: BoatLog Mock Project
**What it does**: Test the entire system with realistic boat 3D reconstruction conversation
**Deliverables**:
- `tests/mock_boatlog.py` (~500-800 lines)
- Simulated user interactions (photo upload, NeRF analysis, mesh optimization)
- Recorded conversation with all ACE tiers represented
- Emergent property metrics (cost savings, decision quality, bot conversion rate)
- Test suite validation

**Dependencies**: Recorder V2 + Bot Engine + Search Engine
**Token cost**: Low (simulation, not real API calls)
**Complexity**: High (realistic scenario design)

**When ready**: Day 2 evening
**Integration point**: Tests all other components together

---

### Phase 1 Timeline (Parallel Work)

```
NOW:           Gemini provides Q1-Q4 answers

DAY 1:
├─ Morning: I parse Gemini's answers
├─ Noon:    Spawn 4 specialist agents
│           ├─ Recorder V2 Agent (works on 1.1)
│           ├─ Bot Engine Agent (works on 1.2)
│           ├─ Search Agent (starts design for 1.3)
│           └─ Test Agent (prepares mock scenarios)
├─ Afternoon: 1.1 and 1.2 complete (parallel)
└─ Evening:  1.1 and 1.2 integrated, tested

DAY 2:
├─ Morning: 1.3 implemented (Search Engine)
├─ Noon:    Final integration of all three
├─ Afternoon: BoatLog mock project runs
└─ Evening: Metrics collected, Phase 1 COMPLETE

PHASE 1 RESULTS:
✓ Recorder V2 working
✓ Bot Engine routing decisions
✓ Search retrieving past decisions
✓ BoatLog conversation recorded with metrics
✓ Emergent properties observed
✓ System proven working end-to-end
```

---

### Phase 1 Success Criteria

- [ ] Recorder captures all conversation tiers (A/C/E)
- [ ] SHL tags generated automatically
- [ ] Consolidation triggered correctly
- [ ] Bot engine converts 3+ E-tier repeats to scripts
- [ ] Search returns relevant past decisions
- [ ] BoatLog runs without errors
- [ ] Token costs tracked and reported
- [ ] At least one emergent property observed (e.g., bot conversion rate > 20%)

---

### Phase 1 Token Budget Estimate

| Component | Estimated Tokens |
|-----------|------------------|
| Recorder V2 design + implementation | 15,000 |
| Bot Engine design + implementation | 8,000 |
| Search Engine design + implementation | 12,000 |
| BoatLog test suite design + implementation | 10,000 |
| Integration and testing | 8,000 |
| Gemini consultation/questions | 5,000 |
| **PHASE 1 TOTAL** | **~58,000 tokens** |

---

## PHASE 2: Real Boat 3D Reconstruction Pipeline

### Duration: ~1-2 weeks of development
### Goal: Build actual NeRF/Gaussian Splatting 3D reconstruction from photos

---

### Phase 2 Components (What Gets Built)

#### 2.1: Photo Ingestion & Preprocessing
**What it does**: Handles input photos, validates quality, extracts metadata
**Deliverables**:
- `core/photo_processor.py`
- EXIF data extraction
- Quality validation (lighting, overlap, resolution)
- Pose estimation initialization
- Storage management

**Depends on**: Phase 1 (meta-framework stable)
**Complexity**: Medium (image processing, EXIF parsing)

---

#### 2.2: NeRF/Gaussian Splatting Implementation
**What it does**: Core 3D reconstruction from multiple views
**Deliverables**:
- `core/reconstruction_engine.py`
- NeRF training pipeline (or Gaussian Splatting)
- Loss functions (photometric, geometric)
- View synthesis validation
- Mesh extraction

**Depends on**: Photo processor, PyTorch setup
**Complexity**: Very High (advanced ML/graphics)
**Token cost**: Low (mostly math, not code generation)

**Note**: This is where you might use Deepseek for architecture suggestions

---

#### 2.3: Unity Integration
**What it does**: Exports 3D models to Unity with LOD and materials
**Deliverables**:
- `core/unity_exporter.py`
- FBX/GLTF export
- Material assignment
- LOD generation
- Scale/coordinate transformation

**Depends on**: Reconstruction engine, mesh data
**Complexity**: Medium (3D formats, coordinate spaces)

---

#### 2.4: Quality Assessment & Feedback Loop
**What it does**: Evaluates reconstruction quality, identifies issues, suggests improvements
**Deliverables**:
- `core/quality_assessor.py`
- F1 score calculation
- Artifact detection
- Completeness metrics
- Feedback generation

**Depends on**: Reconstruction + ground truth data
**Complexity**: Medium (metrics, ML for detection)

---

### Phase 2 Timeline

```
PHASE 1 COMPLETE (End of Day 2)
    ↓
PHASE 2 START (Day 3)

WEEK 1:
├─ Day 3-4: Photo ingestion (2 agents)
├─ Day 4-5: NeRF/Gaussian setup (with research)
└─ Day 5-6: Unity integration

WEEK 2:
├─ Day 7-8: Quality assessment system
├─ Day 8-9: End-to-end testing with sample boat photos
├─ Day 9-10: Optimization and performance tuning
└─ Day 10-14: Polish, documentation, production readiness

PHASE 2 RESULTS:
✓ Can ingest 3-10 boat photos
✓ Produces 3D mesh with reasonable quality
✓ Exports to Unity
✓ Quality metrics show fitness
✓ Can handle different boat types/sizes
✓ Production-ready pipeline
```

---

### Phase 2 Token Budget Estimate

| Component | Estimated Tokens |
|-----------|------------------|
| Photo ingestion system | 12,000 |
| NeRF/Gaussian implementation | 25,000 |
| Unity integration | 8,000 |
| Quality assessment | 10,000 |
| Testing and optimization | 12,000 |
| Research and architecture decisions | 15,000 |
| Deepseek consultation for 3D math | 5,000 |
| **PHASE 2 TOTAL** | **~87,000 tokens** |

---

## TOKEN BUDGET OVERVIEW

### Weekly Token Limits (Typical)
- Claude Code: ~500K tokens/week (very high tier)
- Standard API: ~100K tokens/week

**Assumption**: You have reasonable limits

### Budget Allocation

```
PHASE 1 (2-3 days): 58,000 tokens
  └─ ~20K tokens/day

PHASE 2 (2 weeks): 87,000 tokens
  └─ ~6K tokens/day (spread over 14 days)

TOTAL: 145,000 tokens

Per-week average: 35,000-50,000 tokens
(Safe if you have 100K+/week, very safe if 500K+)
```

---

## TOKEN OPTIMIZATION STRATEGY

### What Burns Tokens Fast (AVOID)
1. **Asking questions without context** - Always provide full context
2. **Iterating on bad architecture** - Decide architecture FIRST
3. **Re-implementing the same thing twice** - Get it right once
4. **Large test suites before code works** - Test as you build
5. **Verbose documentation** - One clear doc, not five

### What Saves Tokens (DO THIS)
1. **Specialized agents** - Each agent focuses on ONE component
2. **Clear specifications before coding** - No "let me try this" iterations
3. **Reuse components** - Don't rebuild from scratch
4. **Efficient testing** - Mock objects, not full systems
5. **Async communication** - Don't wait for responses, work continues
6. **Gemini for architecture** - Uses tokens but prevents wrong implementations

---

## SMART WORK DIVISION

### For Phase 1

**Gemini's role**:
- Answers Q1-Q4 (provides strategic direction)
- Reviews component designs before coding
- Answers architecture questions (prevents wrong approaches)
- Validates integration strategy
- **Estimated cost**: 5-8K tokens

**Claude Code's role**:
- Spawns specialist agents for parallel work
- Coordinates component development
- Handles integration
- Runs test suite
- **Estimated cost**: 50K tokens

**Specialist Agents' roles** (spawned by Claude):
- Recorder V2 Agent: Build persistence layer
- Bot Engine Agent: Build decision routing
- Search Agent: Build retrieval system
- Test Agent: Build validation suite
- **Estimated cost**: ~40K tokens total

---

## THE ACTUAL WORK PLAN

### Right Now: I Ask Gemini for Q1-Q4 Answers
**Cost**: ~3K tokens (context provided, answers extracted)
**Output**: Q1-Q4 in JSON format
**Timeline**: 1-2 hours

### Step 2: Parse Answers, Spawn Agents
**Cost**: ~2K tokens (parsing + agent creation)
**Output**: 4 specialist agents ready to work
**Timeline**: 10 minutes

### Step 3: Parallel Component Development
**Cost**: ~40K tokens (4 agents × 10K each)
**Output**: 4 components complete and tested
**Timeline**: 6-8 hours

### Step 4: Integration & BoatLog Testing
**Cost**: ~10K tokens (integration + test execution)
**Output**: Phase 1 validation complete
**Timeline**: 2 hours

**PHASE 1 TOTAL**: ~55K tokens, ~12 hours

---

## RISK MITIGATION

### Potential Bottleneck 1: Gemini Takes Too Long
**Mitigation**: I've already prepared Q1-Q4 answers based on framework design
**Fallback**: Use my answers, let Gemini verify after Phase 1 starts

### Potential Bottleneck 2: Integration Issues
**Mitigation**: Each agent designs with integration in mind first
**Fallback**: Integration agent is separate, can troubleshoot

### Potential Bottleneck 3: Token Limits Hit
**Mitigation**: Stop detailed logging, use brief status updates only
**Fallback**: Pause Phase 2, resume after token reset

### Potential Bottleneck 4: Agent Quality Issues
**Mitigation**: Gemini reviews design before agents start coding
**Fallback**: Rewrite components manually (higher token cost but correct)

---

## DECISION POINTS

### Before Phase 1 Starts

1. **Should I ask Gemini for Q1-Q4, or use my prepared answers?**
   - Recommendation: Ask Gemini (5K tokens, gets real perspective)

2. **Should I create specialist agents or do it myself?**
   - Recommendation: Spawn agents (saves tokens by parallelizing)

3. **How detailed should component specs be?**
   - Recommendation: Medium detail (clear enough to code, not over-engineered)

4. **Should we do integration as we go or all at the end?**
   - Recommendation: As we go (catch issues early, save tokens on rework)

---

## EXECUTION CHECKLIST

### Before Spawning Agents
- [ ] Gemini provides Q1-Q4 answers (or I confirm using my answers)
- [ ] All component specs written
- [ ] Integration architecture documented
- [ ] Test cases defined
- [ ] Gemini reviews designs (checkpoint)

### During Development
- [ ] Agents report status every 1-2 hours
- [ ] Gemini available for architecture questions (async)
- [ ] No surprises - each agent builds to spec
- [ ] Continuous small tests, not big tests at end

### Before Phase 2
- [ ] BoatLog runs clean
- [ ] All metrics collected
- [ ] Emergent properties documented
- [ ] Lessons learned captured
- [ ] Debrief with Gemini (what worked, what didn't)

---

## SUMMARY

**Phase 1**: Prove the meta-framework works (2-3 days, ~58K tokens)
- Build Recorder V2, Bot Engine, Search System
- Test with BoatLog mock project
- Validate emergent properties

**Phase 2**: Build real 3D reconstruction (2 weeks, ~87K tokens)
- Photo → NeRF/Gaussian Splatting → Unity
- Quality assessment loop
- Production pipeline

**Total tokens**: ~145K (very reasonable)
**Total time**: ~2.5 weeks to complete full system

**Key principle**: Ask Gemini first (prevents wrong implementations), then parallelize work.

---

## READY TO BEGIN?

When you say "GO", I will:
1. Send real Q1-Q4 task to Gemini
2. Wait for answers (1-2 hours max)
3. Spawn 4 specialist agents
4. Begin parallel Phase 1 development
5. Keep you updated with brief status reports

**Token budget is safe. Timeline is realistic. Work is parallelized.**

Ready?
