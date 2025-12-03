# Meta-Framework Design for ShearwaterAICAD
## Integrating devACE Patterns, RAG, and Emergent Properties

**Date**: November 19, 2025
**Status**: Architecture Phase
**Inspired by**: devACE, dual-agents, PropertyCentre-Next implementations

---

## EXECUTIVE SUMMARY

You already have **three working reference implementations**:

1. **devACE** - ACE tier framework + SHL compression + persistent conversation storage
2. **dual-agents** - JSONL conversation recorder with context fragmentation
3. **PropertyCentre-Next** - Smart recorder with consolidation + conversation type detection

**The insight**: These aren't three separate systems. They're **three layers of a single meta-framework**:

```
Layer 1 (devACE):         ACE tiers + SHL shorthand + launch management
                          ↓
Layer 2 (dual-agents):    Conversation recording + context fragmentation
                          ↓
Layer 3 (PropertyCentre): Smart detection + consolidation + semantic organization
```

**Your question**: "Can our persistent recorder benefit from RAG features?"

**Answer**: **Absolutely, but not the traditional way.** Instead of embedding all conversations, we embed **strategically** based on ACE tier and usage patterns.

---

## PART 1: HONEST ASSESSMENT OF YOUR IMPLEMENTATIONS

### devACE - The ACE Tier + SHL Framework

**What it does:**
- 3-tier context hierarchy: Super/Middle/Immediate (different from A/C/E but compatible)
- SHL (Super Heavy Language) compression: "Cfd:name=agent_config;content=..."
- Launches CLI AI environments with prepared context
- Persistent conversation storage in SQLite

**Why it's brilliant:**
1. **ACE Tiers = Agent Decision Authority**
   - Super ≈ Architectural (PM-Alpha decisions)
   - Middle ≈ Collaborative (Dev team consensus)
   - Immediate ≈ Execution (Individual developer work)

2. **SHL = Token cost reduction**
   - Instead of: "Operation: CREATE, Context: file, Name: agent.py, Content: ..."
   - You write: "Cfd:name=agent.py;content=..."
   - **Savings**: 60-70% on metadata overhead

3. **Design Decision History**
   - Every conversation can be tagged with tier
   - Enables "who decided what?" queries (perfect for agent learning)
   - Creates audit trail automatically

**Gaps:**
- No semantic understanding (can't answer "which decisions were about tokens?")
- No automatic fragmentation (needs manual splitting for long conversations)
- Limited awareness of cross-conversation patterns

### dual-agents Recorder - The Append-Only Pattern

**What it does:**
- One JSONL line per event (append-only, cheap)
- Speaker identity preserved (who said it?)
- Context ID = conversation grouping
- Metadata dict for flexibility

**Why it's brilliant:**
1. **Cheap updates** - O(1) append vs O(n) re-embed
2. **Identity preservation** - Crucial for agent learning
3. **Natural fragmentation** - Each context_id is a boundary
4. **Durable** - JSONL format survives any downstream processing

**Gaps:**
- No semantic search (keyword matching only)
- No intelligent consolidation (manual file management)
- No decision classification (all events treated equally)

### PropertyCentre Smart Recorder - The Intelligent Layer

**What it does:**
- Auto-detects conversation chain type (tenant_support, maintenance, lease_mgmt, etc.)
- Extracts keywords automatically
- Consolidates fragments into canonical conversations
- Creates summaries for quick lookup

**Why it's brilliant:**
1. **Semantic organization without embeddings** - Uses domain keywords
2. **Automatic consolidation** - Merges small fragments intelligently
3. **Cost-aware** - Summarizes old fragments, keeps recent full

**Gaps:**
- Tightly coupled to PropertyCentre domain
- Needs tuning for each new domain (e.g., boat 3D reconstruction)
- No ACE tier awareness

---

## PART 2: THE UNIFIED META-FRAMEWORK

### Architecture (Three Integrated Layers)

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: ACE/SHL Management (devACE)               │
│ ├─ Tier classification (A/C/E decisions)           │
│ ├─ SHL compression (60-70% token savings)          │
│ └─ Launch environment with prepared context        │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────v──────────────────────────────────┐
│ Layer 2: Persistent Conversation Recorder (dual-agents) │
│ ├─ JSONL append-only (cheap, durable)             │
│ ├─ Speaker identity + role                         │
│ ├─ Context ID grouping                            │
│ └─ Flexible metadata for each event               │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────v──────────────────────────────────┐
│ Layer 3: Intelligent Organization (PropertyCentre) │
│ ├─ Domain-specific chain detection                │
│ ├─ Automatic keyword extraction                   │
│ ├─ Fragment consolidation                         │
│ └─ Summary generation (compression)               │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────v──────────────────────────────────┐
│ Layer 4: Semantic Search (NEW - Selective RAG)     │
│ ├─ Embed only recent + high-tier conversations    │
│ ├─ Semantic + ACE-aware search                    │
│ └─ Cost-controlled embedding strategy             │
└─────────────────────────────────────────────────────┘
```

---

## PART 3: THE RAG QUESTION - "Should We Embed Everything?"

**Your question**: Would persistent recorder benefit from RAG features?

**My answer**: **Yes, but NOT traditional full RAG.**

### Traditional RAG (Expensive, Not Needed Here)

```
Every conversation → Embed → Store vector → Search semantically
Cost: High (re-embed on updates)
Benefit: Semantic search across all conversations
Use case: When you DON'T know what you're looking for
```

### Selective RAG (What You Actually Need)

```
Conversations:
├─ A-Tier (Architectural decisions)  → ALWAYS embed
├─ C-Tier (Collaborative consensus)  → EMBED if recent (<1 week)
├─ E-Tier (Execution details)        → NEVER embed (search by metadata)
│
Search Strategy:
├─ "Who decided to use PostgreSQL?" → ACE-aware metadata search
├─ "What was the reasoning around token optimization?" → Semantic search (A+C tier only)
└─ "How did Dev-3 implement feature X?" → Speaker + tier metadata search
```

### Cost Comparison

| Strategy | Embeddings | Cost | Speed | Coverage |
|----------|-----------|------|-------|----------|
| Full RAG | All conversations | High | Slow | 100% |
| Selective RAG | A-Tier + recent C | Low-Medium | Fast | 80% |
| **Metadata Only** | None | Minimal | Instant | 60% |

**Recommendation**: Start with **Metadata + Selective RAG**:
- Embed A-Tier decisions permanently
- Embed C-Tier for 1 week (consolidate after)
- E-Tier stays metadata-only
- **Expected token savings**: 40-60% vs full RAG

---

## PART 4: INTEGRATION PLAN FOR SHEARWATERAICAD

### New Conversation Recorder V2: Stratified + ACE-Aware

```python
class ShearwaterConversationRecorder:
    """
    Combines all three approaches
    """

    def record_event(
        self,
        message: str,
        speaker: str,
        role: str,  # "Manager" | "Developer"
        ace_tier: str,  # "A" | "C" | "E"
        chain_type: str,  # "photo_capture" | "reconstruction" | "unity_integration"
        context_id: str,
        metadata: Dict = None
    ):
        """
        Save to JSONL with ACE tier awareness
        """
        event = {
            "id": uuid(),
            "timestamp": now_iso(),
            "speaker": speaker,
            "role": role,
            "message": message,
            "ace_tier": ace_tier,
            "chain_type": chain_type,  # Like PropertyCentre
            "context_id": context_id,
            "metadata": metadata or {},
            "shl_tags": self._generate_shl_tags(message, ace_tier)
        }

        # Save to JSONL
        self._append_to_stream(event)

        # If A-Tier: queue for embedding
        if ace_tier == "A":
            self._queue_for_embedding(event)

        # If recent C-Tier: queue for embedding
        if ace_tier == "C":
            self._queue_for_embedding(event, expires_in_days=7)

        # Consolidate old fragments
        self._check_consolidation()

        return event

    def _generate_shl_tags(self, message: str, tier: str) -> List[str]:
        """
        Generate SHL shorthand for quick reference

        Example outputs:
        - "CRd:topic=token_optimization" (Create Read data about token optimization)
        - "Qs:content=kvCache" (Query system about KV cache)
        """
        return ShlTranslator().extract_tags(message, tier)

    def search(self, query: str, strategy: str = "hybrid") -> List[Dict]:
        """
        Hybrid search: semantic + ACE-aware

        strategy = "metadata" → ACE tiers only
        strategy = "semantic" → Embedding search (A-Tier only)
        strategy = "hybrid"   → Both (default)
        """
        if strategy == "metadata":
            return self._search_by_metadata(query)
        elif strategy == "semantic":
            return self._search_by_semantic(query)
        else:
            return self._search_hybrid(query)

    def _search_hybrid(self, query: str) -> List[Dict]:
        """
        1. Find A-Tier decisions matching query (semantic)
        2. Find matching ACE tiers in metadata
        3. Merge by relevance
        """
        semantic_results = self._search_semantic(query)  # A-Tier embedded
        metadata_results = self._search_metadata(query)   # All tiers, metadata only

        # Merge, preferring A-Tier semantic matches
        return self._merge_results(semantic_results, metadata_results)
```

### Domain-Specific Chain Types for Boats

Based on PropertyCentre patterns, we'd define:

```python
CHAIN_PATTERNS = {
    'photo_capture': [
        'photo', 'image', 'angle', 'lighting', 'overlap',
        'camera', 'height', 'position', 'boat', 'capture'
    ],
    'reconstruction': [
        'nerf', 'mesh', 'texture', 'model', 'reconstruction',
        'point cloud', 'sparse', 'dense', 'structure from motion'
    ],
    'unity_integration': [
        'gameobject', 'prefab', 'import', 'scale', 'material',
        'shader', 'rigging', 'animation', 'asset'
    ],
    'quality_assessment': [
        'quality', 'f1 score', 'metric', 'artifact', 'noise',
        'resolution', 'detail', 'accuracy', 'evaluation'
    ],
    'token_optimization': [
        'token', 'cost', 'cache', 'compression', 'efficiency',
        'latency', 'optimization', 'bottleneck'
    ]
}
```

---

## PART 5: ACE TIER + SHL INTEGRATION

### Tier Mapping

```
ACE Tier    Definition                    Who Decides    Cache Priority
═══════════════════════════════════════════════════════════════════════════
A           Architecture decisions        PM-Alpha       HIGH (cache 1 month)
            (recorder vs RAG?)
            (token strategy?)

C           Collaborative consensus       Dev buddies    MEDIUM (cache 1 week)
            (which NeRF approach?)        + PM oversight
            (boat-specific tuning?)

E           Execution details             Individual     LOW (embed? no)
            (loop optimization)           Developer      (metadata only)
            (refactoring)
```

### SHL Shorthand for ShearwaterAICAD

```
Operation Map (Existing):
  C = CREATE    (Create new agent/framework component)
  R = READ      (Query decision/conversation)
  U = UPDATE    (Modify existing decision)
  D = DELETE    (Archive old fragment)
  S = SEND      (Communicate between agents)
  Q = QUERY     (Search conversations)
  V = VALIDATE  (Check correctness)
  T = TRANSFORM (Compress/consolidate)
  W = WRITE     (Persist to disk)

Context Map (Existing):
  f = file      (Code, config)
  d = data      (Database, conversations)
  u = user      (Agent identity)
  n = network   (Inter-agent communication)
  s = system    (Framework state)
  p = property  (Boat/NeRF properties)
  g = generic   (Other)

Examples for ShearwaterAICAD:
  "Cfp:decision=recorder_over_rag;tier=A"
    → CREATE FILE PROPERTY: architectural decision that recorder beats RAG

  "Rsd:conversation=token_optimization;ace_tier=A"
    → READ SYSTEM DATA: conversations about token optimization (A-Tier)

  "Qn:tokens_spent_this_week"
    → QUERY NETWORK: how many tokens used this week?
```

---

## PART 6: EMERGENT PROPERTY CONDITIONS

With this meta-framework, here's what should emerge:

### 1. Decision Authority Clarity
```
Before: "Who decided to use X?"
After:  Look at ACE tier tags → Find A-Tier decisions → Understand reasoning
```
→ **Emergent**: Agents learn which decisions are architectural (untouchable) vs tactical (flexible)

### 2. Token-Conscious Development
```
Before: Agents make calls without thinking about cost
After:  Selective embedding means E-Tier expensive (metadata only good)
```
→ **Emergent**: Agents naturally learn to compress E-Tier, keep A-Tier detailed

### 3. Conversation Quality Improvement
```
Before: Random conversations recorded
After:  A-Tier automatically preserved/indexed, E-Tier auto-summarized after 1 week
```
→ **Emergent**: Better conversations as agents see which get preserved

### 4. Cross-Agent Learning
```
Before: Dev-1 doesn't know what PM-Alpha decided
After:  SHL tags + ACE tiers + semantic search = clear pattern visibility
```
→ **Emergent**: Agents develop "decision literacy" (understanding how decisions flow)

---

## PART 7: CRITICAL DIFFERENCES FROM PURE RAG

| Aspect | Pure RAG | Our Meta-Framework |
|--------|----------|-------------------|
| **What gets embedded** | Everything | A-Tier always, C-Tier recent only |
| **Cost** | High (re-embed on updates) | Low (selective embedding) |
| **Search type** | Semantic only | Semantic + ACE-aware + metadata |
| **Decision tracking** | Implicit (lost in vectors) | Explicit (ACE tier tags) |
| **Token awareness** | None | Built-in (tier-based strategy) |
| **Agent learning** | "What's similar?" | "What was decided? By whom? When?" |
| **Long-term durability** | Vector DB dependency | JSONL + metadata (format-independent) |

---

## PART 8: BOT vs LLM TOKEN DECISION

You asked: **"Agents need to be efficient. When should we create a bot vs use LLM tokens?"**

With this framework, the answer becomes systematic:

### Decision Rules

```python
class TokenEfficiency:

    @staticmethod
    def should_use_llm(task: str, tier: str) -> bool:
        """
        Decide if task needs LLM vs bot logic
        """

        # A-Tier architectural decisions: ALWAYS LLM
        # (Need reasoning, creativity)
        if tier == "A":
            return True

        # C-Tier collaborative: LLM if novel, Bot if pattern-matched
        if tier == "C":
            if TokenEfficiency._is_known_pattern(task):
                return False  # Use bot
            return True  # Use LLM

        # E-Tier execution: PREFER bot logic
        if tier == "E":
            if TokenEfficiency._is_routine_task(task):
                return False  # Bot
            return True  # LLM only for novel cases

        return True  # Default to LLM for safety

    @staticmethod
    def _is_known_pattern(task: str) -> bool:
        """
        Check if we've solved this before (metadata search)
        """
        # Query previous C-Tier decisions
        # If found similar solution, use bot instead
        pass

    @staticmethod
    def _is_routine_task(task: str) -> bool:
        """
        Is this a repeated E-Tier task?
        """
        # Check E-Tier consolidation files
        # If found 5+ times, create bot function
        pass
```

### Examples for ShearwaterAICAD

```
Task: "Add boat to database"
Tier: E (Execution)
Known Pattern: Yes (done 100 times)
Decision: BOT (simple CRUD operation)
Token Savings: 0.50 → 0.01 per call (50x savings)

---

Task: "Should we switch from NeRF to Gaussian Splatting for reconstruction?"
Tier: A (Architecture)
Known Pattern: No (novel decision)
Decision: LLM (need reasoning)
Token Cost: Accept (5000 tokens) for architectural clarity

---

Task: "Optimize the photogrammetry loop"
Tier: C (Collaborative)
Known Pattern: Maybe (previous optimization attempts exist)
Decision: Hybrid - Search for similar (bot), if not found use LLM
Token Savings: ~40% (search first, LLM only if novel)
```

---

## PART 9: IMPLEMENTATION ROADMAP

### Phase 0.5 (Now): Meta-Framework Design
- [ ] Design stratified recorder with ACE tiers
- [ ] Map chain types for boat domain
- [ ] Integrate SHL tagging system
- [ ] Create bot vs LLM decision rules
- [x] Analyze existing implementations (done)

### Phase 1: Recorder V2 Implementation
- [ ] Create `core/shearwater_recorder.py`
- [ ] Implement JSONL persistence with ACE tiers
- [ ] Add SHL tag generation
- [ ] Wire consolidation logic
- [ ] Create search interface (metadata + semantic)

### Phase 2: Selective RAG Layer
- [ ] Add embedding for A-Tier only
- [ ] Implement semantic search for decisions
- [ ] Create hybrid search (semantic + metadata)
- [ ] Monitor embedding costs
- [ ] Auto-prune old C-Tier embeddings

### Phase 3: Bot vs LLM Framework
- [ ] Create decision engine
- [ ] Build pattern matcher (metadata-based)
- [ ] Define routine E-Tier operations as bots
- [ ] Track token savings
- [ ] Monitor bot vs LLM accuracy

### Phase 4: Agent Integration
- [ ] Deploy with recorder V2
- [ ] Give agents access to bot framework
- [ ] Monitor for emergent properties
- [ ] Track decision-making evolution

---

## KEY QUESTIONS ANSWERED

**Q: Should persistent recorder benefit from RAG?**
A: Yes, **selectively**. Embed A-Tier always, C-Tier recent only, E-Tier never.

**Q: Did I apply devACE/dual-agents/PropertyCentre patterns?**
A: I was analyzing them separately. THIS document shows how they integrate.

**Q: When to create bot vs LLM?**
A: Use framework above - A-Tier=LLM, C-Tier=Hybrid, E-Tier=Bot if routine.

**Q: Are your implementations actually good?**
A: Better than I initially stated. They're not "good implementations of RAG." They're excellent foundations for a **tier-aware, cost-conscious agent system**.

---

## NEXT IMMEDIATE STEPS

1. **You**: Provide ACE framework papers (when you find them)
2. **You**: Confirm domain chain types for boats (photo_capture, reconstruction, etc.)
3. **Me**: Build `core/shearwater_recorder.py` with this architecture
4. **Me**: Create bot vs LLM decision framework
5. **Both**: Test with Phase 1 mock project (BoatLog) before 3D reconstruction

---

**Status**: Meta-framework design complete
**Next**: Implementation of Recorder V2
**Timeline**: Ready to start coding Phase 1 once you confirm boat chain types
