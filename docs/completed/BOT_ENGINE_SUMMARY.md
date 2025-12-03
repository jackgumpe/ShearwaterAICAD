# Bot Engine Design - Executive Summary

**Component**: Bot Engine (Decision Routing System)
**Status**: Design Complete - Ready for Gemini Review
**Author**: Bot Engine Specialist Agent
**Token Budget**: ~8K tokens for implementation

---

## What This Component Does

The Bot Engine is a **decision routing system** that answers one question:

**"Should we use a bot or an LLM for this task?"**

It does NOT implement bots. It makes the strategic decision of which execution path to take.

---

## How It Works

```
Task arrives → Bot Engine analyzes:
  ├─ What tier? (A/C/E)
  ├─ Have we done this before? (pattern matching)
  ├─ How many times? (repeat counter)
  └─ How confident are we? (scoring)

Decision:
  ├─ use_bot=True  → Route to BotRegistry
  └─ use_bot=False → Route to LLM API
```

---

## Tier-Based Routing Rules

**A-Tier (Architectural)**:
- Always LLM (needs reasoning)
- Example: "Should we use NeRF or Gaussian Splatting?"

**C-Tier (Collaborative)**:
- Hybrid: Check if we've solved similar problem before
- If yes (confidence > 0.85): Use bot to retrieve cached solution
- If no: Use LLM for novel problem

**E-Tier (Execution)**:
- Bot after 5 repeats
- Example: "Add boat to database" - first 5 times use LLM, then automate

---

## Key Metrics

**Target**: 20%+ bot conversion rate
**Expected Savings**: 46,800 tokens/month (at 20% conversion)
**ROI**: 5.85x return in first month

**Token Costs**:
- E-Tier LLM: ~100 tokens
- E-Tier Bot: ~15 tokens
- Savings: 85 tokens per conversion (85% reduction)

---

## Dependencies

1. **Recorder V2**: Provides pattern history
2. **Search Engine**: Provides semantic similarity matching
3. **BotRegistry**: Executes bots (separate component)

---

## Success Criteria

- Bot conversion rate > 20%
- False positive rate < 5%
- Decision latency < 100ms
- Token savings > 40,000/month

---

## Questions for Gemini

1. Is 5 repeats the right threshold for E-Tier?
2. Should thresholds vary by chain_type (photo_capture vs reconstruction)?
3. Is 7-day time window appropriate for repeat counting?
4. Are token cost estimates realistic?
5. What additional safeguards needed to prevent false positives?

---

## Implementation Plan

**Code**: `core/bot_engine.py` (~250-300 lines)
**Timeline**: 3-4 hours
**Testing**: Via BoatLog mock project

**Core Class**:
```python
class BotEngine:
    def should_use_bot(task, tier, chain_type) -> RoutingDecision
```

**Output**:
```python
@dataclass
class RoutingDecision:
    use_bot: bool
    confidence: float
    rationale: str
    pattern_match_count: int
    estimated_token_savings: int
    recommended_bot: str
```

---

## Next Steps

1. Gemini reviews design document
2. Address architectural feedback
3. Implement `core/bot_engine.py`
4. Integration test with Recorder V2 + Search Engine
5. Validate with BoatLog

---

**Full Design Document**: `BOT_ENGINE_ARCHITECTURE_DESIGN.md` (2,500 words, comprehensive)
