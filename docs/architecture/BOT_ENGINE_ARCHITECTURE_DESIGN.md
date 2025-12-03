# Bot Engine Architecture Design
## Decision Routing System for Token Optimization in ShearwaterAICAD

**Author**: Bot Engine Specialist Agent (Claude Code)
**Date**: November 19, 2025
**Status**: Design Phase - Awaiting Gemini Review
**Component**: Bot Engine (Phase 1, Component 2)
**Supervisor**: Gemini CLI

---

## Executive Summary

The Bot Engine is a **decision routing system** that determines when to use deterministic bot functions versus expensive LLM token calls for task execution in ShearwaterAICAD. This component does NOT implement the bots themselves - it makes the strategic decision of which execution path to take.

**Core Value Proposition**: Achieve 20%+ bot conversion rate while maintaining quality, resulting in estimated 40-60% token cost reduction for routine E-Tier tasks.

**Key Insight**: Not all tasks require LLM reasoning. By identifying patterns in conversation history and applying tier-based heuristics, we can route routine execution tasks to deterministic functions while reserving LLM capacity for novel problems and architectural decisions.

**Integration Points**:
- **Input**: Task description, ACE tier, conversation context
- **Dependencies**: Recorder V2 (for pattern history), Search Engine (for similarity matching)
- **Output**: Boolean decision (use_bot: True/False) + confidence score + routing rationale

**Token Budget**: ~8K tokens for design and implementation

---

## 1. System Architecture

### 1.1 Component Purpose

The Bot Engine sits at the **decision boundary** between task assignment and task execution:

```
Task Assignment (from PM/Dev agents)
         ↓
   [Bot Engine]  ← Queries Recorder V2 for pattern history
         ↓       ← Queries Search Engine for similar tasks
    Decision:
    ├─ use_bot=True  → Execute via BotRegistry (separate component)
    └─ use_bot=False → Execute via LLM API call
```

**What Bot Engine Does**:
- Analyzes incoming task + tier + context
- Queries conversation history for patterns
- Counts repeats for E-Tier tasks
- Calculates confidence score
- Returns routing decision with justification

**What Bot Engine Does NOT Do**:
- Implement bot functions (that's BotRegistry's job)
- Execute tasks directly
- Store conversation history (that's Recorder V2's job)
- Perform semantic search (that's Search Engine's job)

### 1.2 Input Schema

```python
class TaskRoutingRequest:
    task_description: str       # "Add boat to database with name 'SeaHawk'"
    ace_tier: str              # "A" | "C" | "E"
    chain_type: str            # "photo_capture" | "reconstruction" | etc.
    context_id: str            # Conversation context for history lookup
    metadata: Dict             # Optional: speaker, timestamp, previous attempts
```

### 1.3 Output Schema

```python
class RoutingDecision:
    use_bot: bool              # True = use bot, False = use LLM
    confidence: float          # 0.0-1.0 confidence in decision
    rationale: str             # Human-readable explanation
    pattern_match_count: int   # How many similar tasks found in history
    estimated_token_savings: int  # If bot used, tokens saved
    recommended_bot: str       # If use_bot=True, which bot to invoke
```

### 1.4 Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        Bot Engine                             │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  1. Tier-Based Router                                  │  │
│  │     ├─ A-Tier → Always LLM (architecture needs reasoning)│ │
│  │     ├─ C-Tier → Hybrid (check pattern database)       │  │
│  │     └─ E-Tier → Bot after 5 repeats (execution is routine)││
│  └────────────────────────────────────────────────────────┘  │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  2. Pattern Detection System                           │  │
│  │     ├─ Query Recorder V2 for similar tasks            │  │
│  │     ├─ Fuzzy string matching on task descriptions     │  │
│  │     ├─ Semantic similarity (via Search Engine)        │  │
│  │     └─ Confidence threshold: 0.85 for bot routing     │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  3. Repeat Counter Mechanism (E-Tier only)             │  │
│  │     ├─ Count similar tasks in last 7 days             │  │
│  │     ├─ Threshold: 5 repeats = route to bot            │  │
│  │     ├─ Reset if task pattern changes                  │  │
│  │     └─ Store in Recorder metadata                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                          ↓                                    │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  4. Decision Logic & Confidence Scoring                │  │
│  │     ├─ Combine tier + pattern + repeat count          │  │
│  │     ├─ Calculate confidence (0.0-1.0)                 │  │
│  │     ├─ Generate rationale for transparency            │  │
│  │     └─ Estimate token savings                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
         ↓                    ↓                    ↓
   Recorder V2          Search Engine        BotRegistry
   (pattern history)    (similarity)         (execution)
```

---

## 2. Tier-Based Routing Logic

### 2.1 A-Tier (Architectural Decisions)

**Strategy**: **Always use LLM**

**Rationale**: Architectural decisions require:
- Deep reasoning about system-wide implications
- Creative problem-solving for novel situations
- Trade-off analysis (token cost vs. accuracy vs. maintainability)
- Long-term strategic thinking

**Example A-Tier Tasks**:
- "Should we use NeRF or Gaussian Splatting for boat reconstruction?"
- "How should we structure the agent communication protocol?"
- "What's the optimal balance between embedding cost and search quality?"

**Decision Path**:
```python
if ace_tier == "A":
    return RoutingDecision(
        use_bot=False,
        confidence=1.0,
        rationale="A-Tier architectural decisions always require LLM reasoning",
        pattern_match_count=0,
        estimated_token_savings=0,
        recommended_bot=None
    )
```

**Expected Frequency**: 5-10% of all tasks
**Token Cost**: High (~300-500 tokens per task), but unavoidable and strategically valuable

### 2.2 C-Tier (Collaborative Decisions)

**Strategy**: **Hybrid - LLM for novel, bot if pattern found**

**Rationale**: Collaborative decisions often have precedent. If a similar problem was solved before (e.g., "optimize photogrammetry loop"), we can retrieve that solution instead of re-reasoning.

**Example C-Tier Tasks**:
- "How should we tune NeRF learning rate for boat hulls?" (first time: LLM, subsequent: bot retrieves cached answer)
- "Which quality metrics should we prioritize?" (if discussed before: bot, if novel angle: LLM)
- "Should we batch process photos or stream them?" (pattern-matchable if similar context)

**Decision Path**:
```python
if ace_tier == "C":
    # Query Search Engine for semantically similar C-Tier decisions
    similar_tasks = search_engine.find_similar(
        task_description,
        tier="C",
        chain_type=chain_type,
        similarity_threshold=0.85
    )

    if len(similar_tasks) > 0 and similar_tasks[0].confidence >= 0.85:
        return RoutingDecision(
            use_bot=True,  # Use bot to retrieve cached solution
            confidence=similar_tasks[0].confidence,
            rationale=f"Found {len(similar_tasks)} similar C-Tier decisions in history",
            pattern_match_count=len(similar_tasks),
            estimated_token_savings=200,  # Avg C-Tier LLM cost - bot retrieval cost
            recommended_bot="retrieve_cached_decision"
        )
    else:
        return RoutingDecision(
            use_bot=False,  # Novel problem, use LLM
            confidence=0.7,  # Lower confidence because no precedent
            rationale="No similar C-Tier decision found - using LLM for novel problem",
            pattern_match_count=0,
            estimated_token_savings=0,
            recommended_bot=None
        )
```

**Expected Frequency**: 20-30% of all tasks
**Token Savings Potential**: 40% (if 40% of C-Tier tasks match patterns)

### 2.3 E-Tier (Execution Details)

**Strategy**: **Bot after 5 repeats**

**Rationale**: Execution tasks are inherently routine. After we've solved a task 5 times, we have high confidence the pattern is stable and can be automated.

**Example E-Tier Tasks**:
- "Add boat 'SeaHawk' to database" (repeat #1: LLM, repeat #6: bot)
- "Extract EXIF data from photo" (after 5 successful extractions: bot)
- "Convert mesh to FBX format" (routine after 5 times)

**Decision Path**:
```python
if ace_tier == "E":
    # Count similar E-Tier tasks in last 7 days
    repeat_count = recorder.count_similar_tasks(
        task_description,
        tier="E",
        chain_type=chain_type,
        time_window_days=7
    )

    if repeat_count >= 5:
        return RoutingDecision(
            use_bot=True,
            confidence=min(0.9, 0.5 + (repeat_count * 0.08)),  # Confidence grows with repeats
            rationale=f"E-Tier task repeated {repeat_count} times - routing to bot",
            pattern_match_count=repeat_count,
            estimated_token_savings=90,  # Avg E-Tier LLM cost (~100 tokens) - bot cost (~10 tokens)
            recommended_bot="execute_routine_task"
        )
    else:
        return RoutingDecision(
            use_bot=False,
            confidence=0.8,
            rationale=f"E-Tier task only repeated {repeat_count}/5 times - using LLM until pattern stabilizes",
            pattern_match_count=repeat_count,
            estimated_token_savings=0,
            recommended_bot=None
        )
```

**Expected Frequency**: 60-70% of all tasks
**Token Savings Potential**: 90% token reduction per task after bot conversion
**Bot Conversion Target**: 20%+ of E-Tier tasks → bots

---

## 3. Pattern Detection System

### 3.1 Problem Definition

**Challenge**: How do we identify if a task has been solved before?

Two tasks may have different wording but same intent:
- "Add boat SeaHawk to database"
- "Insert new boat entry for SeaHawk"
- "Create database record: boat_name=SeaHawk"

**Solution**: Multi-level matching strategy

### 3.2 Fuzzy String Matching (Level 1)

**Purpose**: Catch obvious textual similarities
**Library**: `difflib.SequenceMatcher` (Python stdlib, no dependencies)
**Threshold**: 0.75 similarity = potential match

```python
from difflib import SequenceMatcher

def fuzzy_match_score(task1: str, task2: str) -> float:
    """
    Returns 0.0-1.0 similarity score
    """
    return SequenceMatcher(None, task1.lower(), task2.lower()).ratio()

# Example:
fuzzy_match_score(
    "Add boat SeaHawk to database",
    "Insert boat SeaHawk into db"
)
# Returns: 0.73 (close, but below 0.75 threshold)
```

**Advantages**:
- Fast (O(n) comparison)
- No external dependencies
- Good for catching typos and minor rewording

**Limitations**:
- Misses semantic similarity
- Struggles with different word order

### 3.3 Semantic Similarity (Level 2)

**Purpose**: Understand intent, not just word overlap
**Integration**: Via Search Engine component (uses sentence-transformers)
**Threshold**: 0.85 cosine similarity = strong match

```python
# Search Engine provides this interface
similar_tasks = search_engine.find_similar(
    query="Add boat to database",
    tier="E",
    similarity_threshold=0.85,
    max_results=5
)

# Returns ranked list of similar tasks with confidence scores
```

**Advantages**:
- Captures semantic meaning
- Language-agnostic (handles paraphrasing)
- Leverages pre-trained embeddings

**Limitations**:
- Requires embedding (token cost for A-Tier, but E-Tier uses metadata only)
- Slower than string matching

### 3.4 Hybrid Matching Strategy

**Combined Approach**:
1. First, try fuzzy string matching (fast, cheap)
2. If fuzzy match > 0.75, consider it a match
3. If fuzzy match < 0.75 but > 0.60, escalate to semantic search
4. If semantic similarity > 0.85, confirm match

```python
def is_pattern_match(task_description: str, tier: str, chain_type: str) -> Tuple[bool, float, int]:
    """
    Returns: (is_match, confidence, match_count)
    """
    # Stage 1: Fuzzy matching against recent tasks (cheap)
    recent_tasks = recorder.get_recent_tasks(tier=tier, chain_type=chain_type, limit=50)

    fuzzy_matches = []
    for past_task in recent_tasks:
        score = fuzzy_match_score(task_description, past_task.description)
        if score >= 0.75:
            fuzzy_matches.append((past_task, score))

    if len(fuzzy_matches) >= 3:
        return (True, max(m[1] for m in fuzzy_matches), len(fuzzy_matches))

    # Stage 2: Semantic search if fuzzy inconclusive (more expensive)
    if tier in ["A", "C"]:  # Only for tiers that have embeddings
        semantic_matches = search_engine.find_similar(
            task_description,
            tier=tier,
            similarity_threshold=0.85
        )

        if len(semantic_matches) > 0:
            return (True, semantic_matches[0].confidence, len(semantic_matches))

    # No strong match found
    return (False, 0.0, 0)
```

### 3.5 Confidence Thresholds

| Match Type | Threshold | Confidence | Decision |
|------------|-----------|------------|----------|
| Fuzzy ≥ 0.90 | Very High | 0.95 | Route to bot |
| Fuzzy 0.75-0.90 | Medium | 0.80 | Route to bot |
| Semantic ≥ 0.90 | Very High | 0.95 | Route to bot |
| Semantic 0.85-0.90 | Medium | 0.85 | Route to bot |
| Fuzzy < 0.75 + Semantic < 0.85 | Low | 0.60 | Use LLM (novel task) |

---

## 4. Repeat Counter Mechanism (E-Tier)

### 4.1 Purpose

Track how many times an E-Tier task has been successfully executed to determine when it's safe to automate.

**Key Insight**: We need 5 successful repeats because:
- 1-2 repeats: Could be coincidence
- 3-4 repeats: Pattern emerging, but not proven stable
- 5+ repeats: High confidence the task is routine

### 4.2 Counting Strategy

**Time Window**: Last 7 days
**Rationale**:
- Recent tasks are more relevant (system may have evolved)
- Older patterns may be obsolete
- 7 days captures weekly routines

**Storage**: Metadata in Recorder V2 JSONL

```json
{
  "id": "uuid-12345",
  "timestamp": "2025-11-19T14:30:00Z",
  "task_description": "Add boat to database",
  "ace_tier": "E",
  "chain_type": "data_management",
  "execution_result": "success",
  "metadata": {
    "pattern_signature": "e_tier_db_insert_boat",
    "repeat_count": 6,
    "first_seen": "2025-11-13T10:00:00Z",
    "last_seen": "2025-11-19T14:30:00Z",
    "bot_eligible": true
  }
}
```

### 4.3 Pattern Signature Generation

**Problem**: How do we identify "same task" across different wordings?

**Solution**: Normalize task to signature

```python
def generate_pattern_signature(task_description: str, tier: str, chain_type: str) -> str:
    """
    Create normalized signature for pattern matching

    Examples:
    - "Add boat SeaHawk to database" → "e_tier_db_insert_boat"
    - "Insert boat WaveRunner into db" → "e_tier_db_insert_boat"
    - "Extract EXIF from photo_001.jpg" → "e_tier_photo_extract_exif"
    """
    # Extract key verbs and nouns
    verbs = extract_verbs(task_description)  # ["add", "insert", "create"]
    nouns = extract_nouns(task_description)  # ["boat", "database"]

    # Normalize to canonical form
    canonical_verb = normalize_verb(verbs[0])  # "add" | "insert" → "insert"
    canonical_noun = normalize_noun(nouns[0])  # "database" | "db" → "db"

    # Generate signature
    return f"{tier.lower()}_tier_{chain_type}_{canonical_verb}_{canonical_noun}"
```

### 4.4 Counting Logic

```python
def count_repeats(task_description: str, tier: str, chain_type: str, time_window_days: int = 7) -> int:
    """
    Count similar tasks in time window
    """
    # Generate signature for this task
    signature = generate_pattern_signature(task_description, tier, chain_type)

    # Query Recorder for tasks with same signature in last 7 days
    cutoff_date = datetime.now() - timedelta(days=time_window_days)

    matching_tasks = recorder.query(
        pattern_signature=signature,
        tier=tier,
        timestamp_after=cutoff_date,
        execution_result="success"  # Only count successful executions
    )

    return len(matching_tasks)
```

### 4.5 Reset Conditions

**When does the counter reset to zero?**

1. **Task pattern changes**: If task parameters significantly differ
   - Example: "Add boat to database" → "Add boat to database with validation"
   - New signature generated, counter starts fresh

2. **Execution failures**: If task starts failing, counter resets
   - Example: 5 successful executions, then 2 failures → reset to 0
   - Prevents automating broken patterns

3. **Time gap**: If task hasn't been executed in 14 days
   - Rationale: Old patterns may be obsolete
   - Counter resets to avoid stale automation

4. **Manual override**: If user explicitly marks pattern as obsolete
   - Admin can flag patterns for reset

```python
def should_reset_counter(signature: str) -> bool:
    """
    Check if counter should reset
    """
    recent_tasks = recorder.get_tasks_by_signature(signature, limit=10)

    # Check for recent failures
    recent_failures = [t for t in recent_tasks if t.execution_result == "failure"]
    if len(recent_failures) >= 2:
        return True

    # Check for time gap
    if recent_tasks:
        last_execution = max(t.timestamp for t in recent_tasks)
        if (datetime.now() - last_execution).days > 14:
            return True

    # Check for manual override
    if recorder.is_pattern_marked_obsolete(signature):
        return True

    return False
```

---

## 5. Token Economics

### 5.1 Cost Model

**LLM Token Costs (estimated per task)**:
- A-Tier: 300-500 tokens (complex reasoning, multi-step analysis)
- C-Tier: 150-250 tokens (collaborative discussion, solution retrieval)
- E-Tier: 80-120 tokens (execution instructions, parameter passing)

**Bot Costs (estimated per task)**:
- Bot execution: ~10 tokens (function call overhead, result logging)
- Pattern matching: ~5 tokens (fuzzy/semantic lookup)
- Total bot cost: ~15 tokens per execution

**Token Savings per Bot Conversion**:
- E-Tier: 100 tokens (avg) - 15 tokens = **85 tokens saved (85% reduction)**
- C-Tier: 200 tokens (avg) - 15 tokens = **185 tokens saved (92% reduction)**

### 5.2 Break-Even Analysis

**Question**: How many bot conversions needed to break even on Bot Engine development cost?

**Bot Engine Development Cost**: ~8,000 tokens (design + implementation)

**Break-even calculation**:
```
Break-even conversions = 8,000 tokens / 85 tokens per E-tier conversion
                       = ~94 E-Tier bot conversions

OR

Break-even conversions = 8,000 tokens / 185 tokens per C-tier conversion
                       = ~43 C-Tier bot conversions
```

**Expected Timeline to Break-Even**:
- If 10 E-Tier tasks/day convert to bots → break even in **10 days**
- If 5 C-Tier tasks/day convert to bots → break even in **9 days**
- Mixed scenario (7 E-Tier + 3 C-Tier/day) → break even in **7 days**

### 5.3 Target Metrics

**20% Bot Conversion Rate (Gemini's Target)**:
- Assume 100 tasks/day total
- 70% E-Tier (70 tasks)
- 20% C-Tier (20 tasks)
- 10% A-Tier (10 tasks)

**If 20% of E-Tier convert to bots**:
- 14 E-Tier bots/day
- 14 × 85 tokens = **1,190 tokens saved/day**
- 1,190 × 30 days = **35,700 tokens saved/month**

**If 10% of C-Tier convert to bots**:
- 2 C-Tier bots/day
- 2 × 185 tokens = **370 tokens saved/day**
- 370 × 30 days = **11,100 tokens saved/month**

**Total Monthly Savings (at 20% bot conversion)**:
- 35,700 + 11,100 = **46,800 tokens/month**
- **Return on Investment**: 46,800 / 8,000 = **5.85x ROI in first month**

### 5.4 Long-Term Projections

**Month 1**: 20% bot conversion → 46,800 tokens saved
**Month 2**: 30% bot conversion (more patterns learned) → 70,200 tokens saved
**Month 3**: 40% bot conversion (mature system) → 93,600 tokens saved

**Cumulative savings over 3 months**: 210,600 tokens
**ROI**: 210,600 / 8,000 = **26x return in 3 months**

---

## 6. Implementation Plan

### 6.1 Class Structure

```python
# File: core/bot_engine.py

from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher

@dataclass
class RoutingDecision:
    use_bot: bool
    confidence: float
    rationale: str
    pattern_match_count: int
    estimated_token_savings: int
    recommended_bot: Optional[str]

class BotEngine:
    """
    Decision routing engine for bot vs LLM task execution
    """

    def __init__(self, recorder, search_engine):
        self.recorder = recorder
        self.search_engine = search_engine

        # Configuration
        self.E_TIER_BOT_THRESHOLD = 5  # Repeats before bot conversion
        self.FUZZY_MATCH_THRESHOLD = 0.75
        self.SEMANTIC_MATCH_THRESHOLD = 0.85
        self.TIME_WINDOW_DAYS = 7

    def should_use_bot(
        self,
        task_description: str,
        ace_tier: str,
        chain_type: str,
        context_id: str,
        metadata: Optional[Dict] = None
    ) -> RoutingDecision:
        """
        Main decision-making method
        """
        # A-Tier: Always LLM
        if ace_tier == "A":
            return self._route_a_tier(task_description)

        # C-Tier: Hybrid (pattern-based)
        elif ace_tier == "C":
            return self._route_c_tier(task_description, chain_type)

        # E-Tier: Bot after 5 repeats
        elif ace_tier == "E":
            return self._route_e_tier(task_description, chain_type)

        # Default: LLM (safety fallback)
        else:
            return RoutingDecision(
                use_bot=False,
                confidence=0.5,
                rationale=f"Unknown tier '{ace_tier}' - defaulting to LLM",
                pattern_match_count=0,
                estimated_token_savings=0,
                recommended_bot=None
            )

    def _route_a_tier(self, task_description: str) -> RoutingDecision:
        """A-Tier always uses LLM"""
        return RoutingDecision(
            use_bot=False,
            confidence=1.0,
            rationale="A-Tier architectural decisions require LLM reasoning",
            pattern_match_count=0,
            estimated_token_savings=0,
            recommended_bot=None
        )

    def _route_c_tier(self, task_description: str, chain_type: str) -> RoutingDecision:
        """C-Tier: Check for pattern matches"""
        is_match, confidence, match_count = self._is_pattern_match(
            task_description,
            tier="C",
            chain_type=chain_type
        )

        if is_match and confidence >= self.SEMANTIC_MATCH_THRESHOLD:
            return RoutingDecision(
                use_bot=True,
                confidence=confidence,
                rationale=f"Found {match_count} similar C-Tier decisions (confidence: {confidence:.2f})",
                pattern_match_count=match_count,
                estimated_token_savings=185,
                recommended_bot="retrieve_cached_decision"
            )
        else:
            return RoutingDecision(
                use_bot=False,
                confidence=0.7,
                rationale="No strong C-Tier pattern match - using LLM for novel problem",
                pattern_match_count=match_count,
                estimated_token_savings=0,
                recommended_bot=None
            )

    def _route_e_tier(self, task_description: str, chain_type: str) -> RoutingDecision:
        """E-Tier: Bot after 5 repeats"""
        repeat_count = self._count_repeats(task_description, "E", chain_type)

        if repeat_count >= self.E_TIER_BOT_THRESHOLD:
            confidence = min(0.95, 0.5 + (repeat_count * 0.08))
            return RoutingDecision(
                use_bot=True,
                confidence=confidence,
                rationale=f"E-Tier task repeated {repeat_count} times - routing to bot",
                pattern_match_count=repeat_count,
                estimated_token_savings=85,
                recommended_bot="execute_routine_task"
            )
        else:
            return RoutingDecision(
                use_bot=False,
                confidence=0.8,
                rationale=f"E-Tier task only repeated {repeat_count}/{self.E_TIER_BOT_THRESHOLD} times",
                pattern_match_count=repeat_count,
                estimated_token_savings=0,
                recommended_bot=None
            )

    def _is_pattern_match(
        self,
        task_description: str,
        tier: str,
        chain_type: str
    ) -> Tuple[bool, float, int]:
        """
        Hybrid pattern matching: fuzzy + semantic
        """
        # Stage 1: Fuzzy matching (fast)
        recent_tasks = self.recorder.get_recent_tasks(
            tier=tier,
            chain_type=chain_type,
            limit=50
        )

        fuzzy_matches = []
        for past_task in recent_tasks:
            score = self._fuzzy_match_score(task_description, past_task.description)
            if score >= self.FUZZY_MATCH_THRESHOLD:
                fuzzy_matches.append((past_task, score))

        if len(fuzzy_matches) >= 3:
            max_score = max(m[1] for m in fuzzy_matches)
            return (True, max_score, len(fuzzy_matches))

        # Stage 2: Semantic search (more expensive, only for A/C tier)
        if tier in ["A", "C"]:
            semantic_matches = self.search_engine.find_similar(
                task_description,
                tier=tier,
                similarity_threshold=self.SEMANTIC_MATCH_THRESHOLD
            )

            if len(semantic_matches) > 0:
                return (True, semantic_matches[0].confidence, len(semantic_matches))

        return (False, 0.0, len(fuzzy_matches))

    def _count_repeats(
        self,
        task_description: str,
        tier: str,
        chain_type: str
    ) -> int:
        """
        Count similar E-Tier tasks in time window
        """
        signature = self._generate_pattern_signature(task_description, tier, chain_type)
        cutoff_date = datetime.now() - timedelta(days=self.TIME_WINDOW_DAYS)

        matching_tasks = self.recorder.query(
            pattern_signature=signature,
            tier=tier,
            timestamp_after=cutoff_date,
            execution_result="success"
        )

        return len(matching_tasks)

    def _fuzzy_match_score(self, task1: str, task2: str) -> float:
        """Fuzzy string similarity (0.0-1.0)"""
        return SequenceMatcher(None, task1.lower(), task2.lower()).ratio()

    def _generate_pattern_signature(
        self,
        task_description: str,
        tier: str,
        chain_type: str
    ) -> str:
        """
        Generate normalized signature for pattern matching
        Simple version: lowercase + remove stopwords + sort words
        Advanced version: NLP-based verb/noun extraction
        """
        # Simple implementation for MVP
        words = task_description.lower().split()
        stopwords = {"the", "a", "an", "to", "in", "on", "at", "for", "with"}
        filtered_words = [w for w in words if w not in stopwords]
        sorted_words = "_".join(sorted(filtered_words[:5]))  # Take first 5 keywords

        return f"{tier.lower()}_tier_{chain_type}_{sorted_words}"
```

### 6.2 Core Methods

**Primary Interface**:
- `should_use_bot()` - Main entry point for routing decisions

**Tier-Specific Routing**:
- `_route_a_tier()` - Always returns False (use LLM)
- `_route_c_tier()` - Pattern-based hybrid routing
- `_route_e_tier()` - Repeat-based bot conversion

**Pattern Detection**:
- `_is_pattern_match()` - Fuzzy + semantic matching
- `_fuzzy_match_score()` - String similarity (0.0-1.0)

**Repeat Tracking**:
- `_count_repeats()` - Query Recorder for similar tasks
- `_generate_pattern_signature()` - Normalize task to signature

### 6.3 Dependencies

**Required Components**:
1. **Recorder V2**: `core/shearwater_recorder.py`
   - Methods needed:
     - `get_recent_tasks(tier, chain_type, limit)`
     - `query(pattern_signature, tier, timestamp_after, execution_result)`

2. **Search Engine**: `core/search_engine.py`
   - Methods needed:
     - `find_similar(query, tier, similarity_threshold)`

3. **BotRegistry**: `core/bot_registry.py` (separate component)
   - Methods needed:
     - `get_bot(bot_name)` - Not used by BotEngine directly, but downstream

**Configuration**:
- `E_TIER_BOT_THRESHOLD = 5` (configurable)
- `FUZZY_MATCH_THRESHOLD = 0.75` (configurable)
- `SEMANTIC_MATCH_THRESHOLD = 0.85` (configurable)
- `TIME_WINDOW_DAYS = 7` (configurable)

---

## 7. Code Outline (Pseudo-Code)

### 7.1 Full Implementation Sketch (~250-300 lines)

```python
# core/bot_engine.py

from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

@dataclass
class RoutingDecision:
    """
    Result of bot vs LLM routing decision
    """
    use_bot: bool
    confidence: float
    rationale: str
    pattern_match_count: int
    estimated_token_savings: int
    recommended_bot: Optional[str]

    def to_dict(self) -> Dict:
        return {
            "use_bot": self.use_bot,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "pattern_match_count": self.pattern_match_count,
            "estimated_token_savings": self.estimated_token_savings,
            "recommended_bot": self.recommended_bot
        }

class BotEngineConfig:
    """Configuration for BotEngine"""
    E_TIER_BOT_THRESHOLD: int = 5
    FUZZY_MATCH_THRESHOLD: float = 0.75
    SEMANTIC_MATCH_THRESHOLD: float = 0.85
    TIME_WINDOW_DAYS: int = 7

    # Token cost estimates
    TOKEN_COST_A_TIER: int = 400
    TOKEN_COST_C_TIER: int = 200
    TOKEN_COST_E_TIER: int = 100
    TOKEN_COST_BOT: int = 15

class BotEngine:
    """
    Decision routing engine for bot vs LLM execution

    Determines when to use deterministic bot functions vs
    expensive LLM token calls based on:
    - ACE tier (A/C/E)
    - Pattern history (via Recorder)
    - Repeat count (for E-Tier)
    - Confidence scoring
    """

    def __init__(self, recorder, search_engine, config: Optional[BotEngineConfig] = None):
        """
        Initialize BotEngine

        Args:
            recorder: ShearwaterConversationRecorder instance
            search_engine: SearchEngine instance for semantic matching
            config: Optional custom configuration
        """
        self.recorder = recorder
        self.search_engine = search_engine
        self.config = config or BotEngineConfig()

        logger.info("BotEngine initialized with config: %s", self.config.__dict__)

    def should_use_bot(
        self,
        task_description: str,
        ace_tier: str,
        chain_type: str,
        context_id: str,
        metadata: Optional[Dict] = None
    ) -> RoutingDecision:
        """
        Main decision-making method

        Args:
            task_description: Natural language task description
            ace_tier: "A" | "C" | "E"
            chain_type: Domain chain (e.g., "photo_capture", "reconstruction")
            context_id: Conversation context for history lookup
            metadata: Optional additional context

        Returns:
            RoutingDecision with use_bot flag and supporting data
        """
        logger.debug("Routing decision for task: %s (tier: %s, chain: %s)",
                     task_description[:50], ace_tier, chain_type)

        # Route based on tier
        if ace_tier == "A":
            decision = self._route_a_tier(task_description)
        elif ace_tier == "C":
            decision = self._route_c_tier(task_description, chain_type)
        elif ace_tier == "E":
            decision = self._route_e_tier(task_description, chain_type)
        else:
            decision = self._route_unknown_tier(ace_tier)

        # Log decision
        logger.info("Decision: use_bot=%s, confidence=%.2f, rationale=%s",
                    decision.use_bot, decision.confidence, decision.rationale)

        # Record decision for future analysis
        self._record_decision(task_description, ace_tier, chain_type, decision)

        return decision

    def _route_a_tier(self, task_description: str) -> RoutingDecision:
        """
        A-Tier routing: Always use LLM

        Architectural decisions require deep reasoning and cannot
        be automated safely.
        """
        return RoutingDecision(
            use_bot=False,
            confidence=1.0,
            rationale="A-Tier architectural decisions require full LLM reasoning",
            pattern_match_count=0,
            estimated_token_savings=0,
            recommended_bot=None
        )

    def _route_c_tier(self, task_description: str, chain_type: str) -> RoutingDecision:
        """
        C-Tier routing: Hybrid - check for pattern matches

        If similar collaborative decision found in history,
        use bot to retrieve cached solution. Otherwise, use LLM.
        """
        # Check for pattern matches
        is_match, confidence, match_count = self._is_pattern_match(
            task_description,
            tier="C",
            chain_type=chain_type
        )

        if is_match and confidence >= self.config.SEMANTIC_MATCH_THRESHOLD:
            # Strong pattern match - use bot to retrieve
            return RoutingDecision(
                use_bot=True,
                confidence=confidence,
                rationale=f"Found {match_count} similar C-Tier decisions with {confidence:.2f} confidence",
                pattern_match_count=match_count,
                estimated_token_savings=self.config.TOKEN_COST_C_TIER - self.config.TOKEN_COST_BOT,
                recommended_bot="retrieve_cached_decision"
            )
        else:
            # No strong match - novel problem, use LLM
            return RoutingDecision(
                use_bot=False,
                confidence=0.7,
                rationale=f"No strong C-Tier pattern match (found {match_count}, confidence {confidence:.2f})",
                pattern_match_count=match_count,
                estimated_token_savings=0,
                recommended_bot=None
            )

    def _route_e_tier(self, task_description: str, chain_type: str) -> RoutingDecision:
        """
        E-Tier routing: Bot after threshold repeats

        Execution tasks are routine. After N successful repeats,
        route to bot for automation.
        """
        # Count repeats in time window
        repeat_count = self._count_repeats(task_description, "E", chain_type)

        if repeat_count >= self.config.E_TIER_BOT_THRESHOLD:
            # Enough repeats - route to bot
            # Confidence grows with repeat count
            confidence = min(0.95, 0.5 + (repeat_count * 0.08))

            return RoutingDecision(
                use_bot=True,
                confidence=confidence,
                rationale=f"E-Tier task repeated {repeat_count} times - safe to automate",
                pattern_match_count=repeat_count,
                estimated_token_savings=self.config.TOKEN_COST_E_TIER - self.config.TOKEN_COST_BOT,
                recommended_bot="execute_routine_task"
            )
        else:
            # Not enough repeats yet - use LLM
            return RoutingDecision(
                use_bot=False,
                confidence=0.8,
                rationale=f"E-Tier task only repeated {repeat_count}/{self.config.E_TIER_BOT_THRESHOLD} times",
                pattern_match_count=repeat_count,
                estimated_token_savings=0,
                recommended_bot=None
            )

    def _route_unknown_tier(self, tier: str) -> RoutingDecision:
        """Fallback for unknown tiers"""
        logger.warning("Unknown tier '%s' - defaulting to LLM", tier)
        return RoutingDecision(
            use_bot=False,
            confidence=0.5,
            rationale=f"Unknown tier '{tier}' - defaulting to LLM for safety",
            pattern_match_count=0,
            estimated_token_savings=0,
            recommended_bot=None
        )

    def _is_pattern_match(
        self,
        task_description: str,
        tier: str,
        chain_type: str
    ) -> Tuple[bool, float, int]:
        """
        Hybrid pattern matching: fuzzy + semantic

        Returns:
            (is_match, confidence, match_count)
        """
        # Stage 1: Fuzzy string matching (fast, cheap)
        recent_tasks = self.recorder.get_recent_tasks(
            tier=tier,
            chain_type=chain_type,
            limit=50
        )

        fuzzy_matches = []
        for past_task in recent_tasks:
            score = self._fuzzy_match_score(task_description, past_task.description)
            if score >= self.config.FUZZY_MATCH_THRESHOLD:
                fuzzy_matches.append((past_task, score))

        # If we have 3+ fuzzy matches, consider it a pattern
        if len(fuzzy_matches) >= 3:
            max_score = max(m[1] for m in fuzzy_matches)
            return (True, max_score, len(fuzzy_matches))

        # Stage 2: Semantic search (more expensive, only for A/C tiers)
        if tier in ["A", "C"]:
            try:
                semantic_matches = self.search_engine.find_similar(
                    task_description,
                    tier=tier,
                    similarity_threshold=self.config.SEMANTIC_MATCH_THRESHOLD
                )

                if len(semantic_matches) > 0:
                    return (True, semantic_matches[0].confidence, len(semantic_matches))
            except Exception as e:
                logger.error("Semantic search failed: %s", e)

        # No strong match found
        return (False, 0.0, len(fuzzy_matches))

    def _count_repeats(
        self,
        task_description: str,
        tier: str,
        chain_type: str
    ) -> int:
        """
        Count similar tasks in time window
        """
        # Generate normalized signature
        signature = self._generate_pattern_signature(task_description, tier, chain_type)

        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=self.config.TIME_WINDOW_DAYS)

        # Query recorder for matching tasks
        try:
            matching_tasks = self.recorder.query(
                pattern_signature=signature,
                tier=tier,
                timestamp_after=cutoff_date,
                execution_result="success"  # Only count successful executions
            )
            return len(matching_tasks)
        except Exception as e:
            logger.error("Error counting repeats: %s", e)
            return 0

    def _fuzzy_match_score(self, task1: str, task2: str) -> float:
        """
        Calculate fuzzy string similarity (0.0-1.0)

        Uses difflib.SequenceMatcher for fast comparison
        """
        return SequenceMatcher(None, task1.lower(), task2.lower()).ratio()

    def _generate_pattern_signature(
        self,
        task_description: str,
        tier: str,
        chain_type: str
    ) -> str:
        """
        Generate normalized signature for pattern matching

        Simple implementation: lowercase + remove stopwords + sort

        Examples:
        - "Add boat SeaHawk to database" → "e_tier_data_management_add_boat_database"
        - "Insert boat WaveRunner into db" → "e_tier_data_management_boat_db_insert"

        TODO: Upgrade to NLP-based verb/noun extraction for better accuracy
        """
        # Stopwords to remove
        stopwords = {"the", "a", "an", "to", "in", "on", "at", "for", "with", "into"}

        # Tokenize and filter
        words = task_description.lower().split()
        filtered_words = [w for w in words if w not in stopwords]

        # Take first 5 keywords and sort for consistency
        keywords = sorted(filtered_words[:5])
        keyword_string = "_".join(keywords)

        # Generate signature
        return f"{tier.lower()}_tier_{chain_type}_{keyword_string}"

    def _record_decision(
        self,
        task_description: str,
        ace_tier: str,
        chain_type: str,
        decision: RoutingDecision
    ):
        """
        Record routing decision for future analysis

        This helps us track:
        - Bot conversion rate
        - Decision accuracy
        - Token savings over time
        """
        try:
            self.recorder.record_event(
                message=f"Bot routing decision: {decision.rationale}",
                speaker="BotEngine",
                role="System",
                ace_tier=ace_tier,
                chain_type=chain_type,
                context_id="bot_engine_decisions",
                metadata={
                    "task_description": task_description,
                    "decision": decision.to_dict(),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error("Failed to record decision: %s", e)

    def get_metrics(self, time_window_days: int = 30) -> Dict:
        """
        Get Bot Engine performance metrics

        Returns:
            - bot_conversion_rate: % of tasks routed to bots
            - total_token_savings: Cumulative tokens saved
            - decisions_by_tier: Breakdown by A/C/E
        """
        cutoff_date = datetime.now() - timedelta(days=time_window_days)

        # Query all bot engine decisions
        decisions = self.recorder.query(
            context_id="bot_engine_decisions",
            timestamp_after=cutoff_date
        )

        total_decisions = len(decisions)
        bot_decisions = sum(1 for d in decisions if d.metadata.get("decision", {}).get("use_bot"))
        total_savings = sum(d.metadata.get("decision", {}).get("estimated_token_savings", 0)
                           for d in decisions)

        return {
            "total_decisions": total_decisions,
            "bot_conversions": bot_decisions,
            "bot_conversion_rate": bot_decisions / total_decisions if total_decisions > 0 else 0,
            "total_token_savings": total_savings,
            "average_savings_per_decision": total_savings / total_decisions if total_decisions > 0 else 0,
            "time_window_days": time_window_days
        }

# Example usage
if __name__ == "__main__":
    # Mock dependencies for testing
    from core.shearwater_recorder import ShearwaterConversationRecorder
    from core.search_engine import SearchEngine

    recorder = ShearwaterConversationRecorder()
    search_engine = SearchEngine()

    bot_engine = BotEngine(recorder, search_engine)

    # Test A-Tier decision
    decision = bot_engine.should_use_bot(
        task_description="Should we use NeRF or Gaussian Splatting?",
        ace_tier="A",
        chain_type="reconstruction",
        context_id="test_context_1"
    )
    print(f"A-Tier decision: {decision.to_dict()}")

    # Test E-Tier decision (first time)
    decision = bot_engine.should_use_bot(
        task_description="Add boat SeaHawk to database",
        ace_tier="E",
        chain_type="data_management",
        context_id="test_context_2"
    )
    print(f"E-Tier decision (first time): {decision.to_dict()}")
```

---

## 8. Success Criteria & Metrics

### 8.1 Primary Success Metrics

**Target 1: Bot Conversion Rate > 20%**
- Measure: `(bot_decisions / total_decisions) × 100`
- Expected: 20-30% in first month, 40%+ by month 3
- How to measure: `bot_engine.get_metrics()`

**Target 2: Token Savings > 40,000/month**
- Measure: `sum(estimated_token_savings)` for all decisions
- Expected: 46,800 tokens/month at 20% conversion rate
- How to measure: Dashboard tracking cumulative savings

**Target 3: False Positive Rate < 5%**
- Measure: Bot decisions that resulted in errors or needed LLM override
- Expected: < 5% of bot decisions fail
- How to measure: Track execution results, count failures after bot routing

**Target 4: Decision Latency < 100ms**
- Measure: Time from `should_use_bot()` call to decision return
- Expected: < 100ms for fuzzy matching, < 500ms if semantic search needed
- How to measure: Instrumentation in BotEngine

### 8.2 Secondary Metrics

**Pattern Match Accuracy**:
- Precision: Of tasks routed to bots, how many were correct decisions?
- Recall: Of tasks that could have been bots, how many did we catch?
- Target: Precision > 90%, Recall > 70%

**Repeat Threshold Validation**:
- Question: Is 5 repeats the right threshold?
- Measure: Track error rate for tasks converted at repeat counts 3, 4, 5, 6, 7
- Adjust: If errors spike at 5, increase threshold

**Tier Distribution**:
- Track: What % of tasks are A/C/E tier?
- Expected: A=10%, C=20%, E=70%
- Use: Validate assumptions about task distribution

### 8.3 Monitoring Dashboard

**Real-time Metrics**:
```python
{
  "bot_conversion_rate": 0.23,  # 23% of tasks routed to bots
  "token_savings_today": 1560,  # Tokens saved today
  "token_savings_month": 42300, # Cumulative for month
  "decisions_by_tier": {
    "A": {"total": 100, "bot": 0},      # A-Tier never uses bots
    "C": {"total": 200, "bot": 20},     # C-Tier: 10% bot conversion
    "E": {"total": 700, "bot": 210}     # E-Tier: 30% bot conversion
  },
  "false_positive_rate": 0.03,  # 3% of bot decisions were wrong
  "average_decision_latency_ms": 85
}
```

### 8.4 Validation Strategy

**Phase 1: BoatLog Testing**
- Run BoatLog mock project
- Record all bot routing decisions
- Manually verify correctness
- Calculate precision/recall

**Phase 2: Shadow Mode**
- Run BotEngine in "shadow mode" (don't actually route to bots yet)
- Compare BotEngine decisions to manual human judgment
- Tune thresholds based on results

**Phase 3: Production Deployment**
- Enable bot routing for E-Tier only (safest tier)
- Monitor error rates closely
- Gradually enable C-Tier bot routing
- A-Tier always stays LLM

### 8.5 Edge Case Testing

**Test Case 1: Novel Task with Similar Wording**
- Task: "Add boat to database with validation checks"
- Previous: "Add boat to database" (repeated 10 times)
- Expected: Should NOT route to bot (pattern changed)
- Test: Verify signature generation detects difference

**Test Case 2: Execution Failure After Bot Conversion**
- Task: "Extract EXIF from photo" (successful 10 times, then fails 2 times)
- Expected: Counter resets, routes back to LLM
- Test: Verify reset logic triggers

**Test Case 3: Time Gap**
- Task: "Generate mesh from NeRF" (successful 10 times, then 15-day gap)
- Expected: Counter resets due to staleness
- Test: Verify time-based reset

**Test Case 4: Semantic Match but Wrong Context**
- Task: "Add boat to test database" (tier: E)
- Previous: "Add boat to production database" (tier: E, 10 times)
- Expected: Should recognize different contexts
- Test: Verify chain_type prevents false match

---

## Appendix A: Integration with Recorder V2

The Bot Engine depends on Recorder V2 for pattern history. Here's the expected interface:

```python
# Expected from core/shearwater_recorder.py

class ShearwaterConversationRecorder:

    def get_recent_tasks(
        self,
        tier: str,
        chain_type: str,
        limit: int = 50
    ) -> List[Task]:
        """
        Get recent tasks matching tier and chain_type

        Returns list of Task objects with:
        - task.description: str
        - task.timestamp: datetime
        - task.execution_result: "success" | "failure"
        """
        pass

    def query(
        self,
        pattern_signature: Optional[str] = None,
        tier: Optional[str] = None,
        timestamp_after: Optional[datetime] = None,
        execution_result: Optional[str] = None,
        context_id: Optional[str] = None
    ) -> List[Task]:
        """
        Flexible query interface for finding matching tasks
        """
        pass

    def record_event(
        self,
        message: str,
        speaker: str,
        role: str,
        ace_tier: str,
        chain_type: str,
        context_id: str,
        metadata: Dict = None
    ):
        """
        Record an event (including bot routing decisions)
        """
        pass
```

---

## Appendix B: Integration with Search Engine

The Bot Engine uses Search Engine for semantic similarity matching:

```python
# Expected from core/search_engine.py

class SearchEngine:

    def find_similar(
        self,
        query: str,
        tier: Optional[str] = None,
        chain_type: Optional[str] = None,
        similarity_threshold: float = 0.85,
        max_results: int = 5
    ) -> List[SimilarTask]:
        """
        Find semantically similar tasks

        Returns list of SimilarTask objects with:
        - task.description: str
        - task.confidence: float (0.0-1.0 cosine similarity)
        - task.tier: str
        - task.chain_type: str
        """
        pass
```

---

## Appendix C: Questions for Gemini Review

As the Bot Engine Specialist, I'd like Gemini's feedback on:

1. **Threshold Validation**: Is 5 repeats the right threshold for E-Tier bot conversion? Should it vary by chain_type?

2. **Pattern Signature Approach**: Is the simple "lowercase + sort + stopword removal" sufficient, or should we invest in NLP-based verb/noun extraction?

3. **C-Tier Strategy**: For collaborative tasks, is semantic search (0.85 threshold) the right approach, or should we use a different strategy?

4. **Time Window**: Is 7 days the right window for repeat counting? Should it be longer for some chain types?

5. **Reset Logic**: Are the reset conditions (failure spike, time gap, manual override) comprehensive enough?

6. **False Positive Mitigation**: What additional safeguards should we add to prevent routing to bots when we shouldn't?

7. **Token Savings Estimates**: Are the token cost estimates (A=400, C=200, E=100, Bot=15) realistic?

---

## Conclusion

The Bot Engine is a **strategic decision router** that achieves token efficiency through tier-aware pattern matching. By implementing this component alongside Recorder V2 and Search Engine, we expect to achieve:

- 20%+ bot conversion rate in first month
- 40,000+ tokens saved per month
- < 5% false positive rate
- Foundation for 40%+ bot conversion by month 3

**Next Steps**:
1. Gemini reviews this design document
2. Address any architectural concerns
3. Begin implementation of `core/bot_engine.py`
4. Integration testing with Recorder V2 and Search Engine
5. Validation via BoatLog mock project

**Estimated Implementation**: 3-4 hours (250-300 lines of Python)
**Token Budget**: ~8K tokens

Ready for Gemini's review and feedback.
