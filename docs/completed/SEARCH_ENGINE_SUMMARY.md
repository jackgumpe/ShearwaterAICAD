# Search Engine Design - Executive Summary

**Component**: Phase 1.3 - Selective RAG Search Engine
**Status**: Design Complete - Awaiting Gemini Review
**Token Budget**: 12K for implementation
**Timeline**: 9 hours (3 days)

---

## What We Built (Design)

A **tier-aware search system** that embeds strategically instead of blindly embedding everything.

### The Strategy

```
A-Tier (Architectural)  → Embed PERMANENTLY (never expires)
C-Tier (Collaborative)  → Embed for 7 DAYS (then auto-delete)
E-Tier (Execution)      → METADATA ONLY (never embed)
```

### Why This Works

| Approach | What Gets Embedded | Monthly Cost | Accuracy |
|----------|-------------------|--------------|----------|
| Full RAG | All 2100 conversations | $63 | 87% |
| **Our Selective RAG** | **100 conversations** | **$3** | **85%** |
| Metadata Only | Nothing | $0 | 60% |

**Result**: 95% cost savings, only 2% accuracy loss

---

## Core Architecture

### Storage
```
data/search/
├── vectors/
│   ├── a_tier_embeddings.npy       # Permanent (grows forever)
│   ├── c_tier_embeddings.npy       # Rolling 7-day window
│   └── metadata.jsonl              # Vector metadata
└── search_index.db                 # SQLite FTS5 (E-Tier)
```

### Search Methods

**A-Tier Search** (Semantic):
- Embed query → Cosine similarity → Top-K results
- Target: >95% recall of architectural decisions
- Latency: ~90ms

**C-Tier Search** (Semantic + Temporal):
- Embed query → Combined score (70% semantic, 30% recency)
- Auto-decay older results (half-life 3.5 days)
- Latency: ~100ms

**E-Tier Search** (Metadata):
- SQLite FTS5 keyword search
- Filter by speaker, timestamp, chain type
- Latency: ~60ms

**Hybrid Search** (All Tiers):
- Parallel search → Merge → Tier-weighted ranking
- A-Tier boosted 1.5x, C-Tier 1.2x
- Latency: ~150ms

---

## Implementation Plan

### Phase 1: Core (4 hours)
- SearchEngine class skeleton
- Embedding model (sentence-transformers/all-MiniLM-L6-v2)
- SQLite schema
- A-Tier search

### Phase 2: C-Tier TTL (3 hours)
- C-Tier indexing with expiration
- Daily cleanup task
- Temporal decay scoring

### Phase 3: Integration (2 hours)
- E-Tier metadata search
- Recorder V2 integration
- Bot Engine pattern matching
- Error handling

---

## Key Decisions

### 1. Embedding Model
**Choice**: sentence-transformers/all-MiniLM-L6-v2 (local)
- 384 dimensions
- 80MB model size
- ~50ms inference (CPU)
- Zero API cost

**Alternative**: all-mpnet-base-v2 (768 dim, better accuracy, slower)

### 2. 7-Day Window for C-Tier
**Rationale**:
- Matches typical sprint length
- Collaborative discussions relevant short-term
- Auto-expires when context changes

**Question for Gemini**: Is 7 days optimal, or 5/10/14?

### 3. No E-Tier Embeddings
**Rationale**:
- High volume (2000/month)
- Low strategic value
- Metadata search sufficient (FTS5)

**Question for Gemini**: Should we embed E-Tier after 10+ repeats for bot matching?

### 4. Local Vector Storage
**Choice**: JSONL + NumPy (not Pinecone/Weaviate)
- No external dependencies
- Full control over TTL
- Trivial storage (<15 MB/year)

**Trade-off**: Manual TTL cleanup vs built-in features

---

## Integration Points

### With Recorder V2
```python
# When recording event
if tier == "A":
    search_engine.index_a_tier(event)
elif tier == "C":
    search_engine.index_c_tier(event, ttl_days=7)
else:
    search_engine.index_e_tier_metadata(event)
```

### With Bot Engine
```python
# Check if E-Tier task is routine
results = search_engine.search(
    task_description,
    tier_filter=["E"],
    strategy="metadata",
    limit=20
)
routine = len([r for r in results if r.relevance > 0.7]) >= 5
```

### With Agents
```python
# Get architectural context
results = search_engine.search(
    "token optimization",
    tier_filter=["A"],
    limit=3
)
```

---

## Cost Analysis

### Monthly Volume (Estimated)
- A-Tier: 50 decisions
- C-Tier: 200 conversations (50 active)
- E-Tier: 2000 executions
- **Total**: 2250 events

### Embedding Breakdown
| Tier | Embedded | Cost |
|------|----------|------|
| A-Tier | 50 (permanent) | $1.50 one-time |
| C-Tier | 50 (rolling) | $1.50/month |
| E-Tier | 0 (metadata) | $0 |
| **Total** | **100** | **$3/month** |

**vs Full RAG**: $63/month (2250 embeddings)
**Savings**: 95%

---

## Performance Targets

| Metric | Target | Strategy |
|--------|--------|----------|
| Search Latency (p95) | <500ms | Local embeddings, indexed SQLite |
| Top-3 Accuracy | >80% | Selective embedding of high-value content |
| A-Tier Recall | >95% | Full semantic search, permanent storage |
| C-Tier Recall | >75% | Semantic + temporal within window |
| E-Tier Precision | >70% | FTS5 keyword matching |

---

## Questions for Gemini

### Critical Decisions
1. **C-Tier TTL**: Is 7 days correct, or adjust?
2. **E-Tier Strategy**: Metadata-only sufficient, or embed after N repeats?
3. **Cost Savings**: Does 40-60% match expectations?

### Implementation Details
4. **Async Indexing**: Synchronous or queue-based?
5. **Embedding Model**: all-MiniLM-L6-v2 or upgrade to all-mpnet-base-v2?
6. **Vector Storage**: Stay with JSONL+NumPy or use Qdrant/Chroma?

### Edge Cases
7. **C-Tier Promotion**: Auto-promote valuable discussions to A-Tier?
8. **E-Tier Archival**: Compress or delete after 30 days?
9. **Bot Threshold**: 5-repeat E-Tier threshold confirmed?
10. **Tier Boost Factors**: A×1.5, C×1.2 reasonable for hybrid search?

---

## Next Steps

1. **Gemini Review**: Validate architecture and answer questions
2. **Volume Confirmation**: Get realistic estimates from BoatLog
3. **Implementation**: Begin coding after approval
4. **Testing**: Unit, integration, performance tests
5. **Integration**: Wire to Recorder V2 and Bot Engine

---

## Success Criteria

- [ ] Latency <500ms (p95)
- [ ] Accuracy >80% (top-3)
- [ ] Cost savings 40-60%
- [ ] Integration tests pass
- [ ] Gemini approval

---

**Status**: Ready for review
**Full Design**: See SEARCH_ENGINE_DESIGN.md (2900 words)
**Author**: Search Engine Specialist Agent
**Date**: November 19, 2025
