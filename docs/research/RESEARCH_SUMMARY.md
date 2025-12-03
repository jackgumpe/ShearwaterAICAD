# Research Summary: Conversation Segmentation & Block Consolidation

## Overview

You identified that 2,367 messages is still too fragmented. The solution: **Conversation Blocks** (1-3 hour coherent units) instead of individual messages. Target: 300-400 blocks from 2,367 messages.

This requires research into:
1. How to detect conversation boundaries algorithmically
2. How to segment by time + topic + ACE tier
3. How vision-language models improve over time
4. How to create intelligent summaries

---

## Key Research Areas

### 1. Conversation Segmentation & Topic Boundary Detection

**What we're looking for:**
- Algorithms that detect when a conversation topic changes
- Methods to identify natural conversation boundaries
- Time-aware clustering (2-hour windows)
- ACE tier-aware segmentation

**Relevant Research Directions:**

**a) Dialogue Act Classification & Topic Segmentation**
- **Technique**: Analyze each message for dialogue acts (question, statement, decision, clarification)
- **Application**: A series of related acts = same conversation block
- **Papers to check**: "Dialogue Act Classification with Dependency Syntax" and similar
- **HuggingFace**: Look for `zero-shot-classification` models that can classify dialogue acts

**b) Semantic Similarity for Continuity**
- **Technique**: Embed messages, compute cosine similarity between consecutive messages
- **Application**: Large similarity drops indicate topic boundaries
- **Models**: `sentence-transformers/all-MiniLM-L6-v2` or `all-mpnet-base-v2`
- **HuggingFace**: Pre-trained models for semantic search

**Example pseudocode:**
```python
embeddings = [embed(msg) for msg in messages]
similarities = [cosine_similarity(embeddings[i], embeddings[i+1])
                for i in range(len(embeddings)-1)]

# When similarity drops below threshold, new block starts
blocks = []
current_block = []
for i, msg in enumerate(messages):
    current_block.append(msg)
    if i < len(similarities) and similarities[i] < THRESHOLD:
        blocks.append(current_block)
        current_block = []
```

**c) Named Entity Recognition (NER) for Topic Identification**
- **Technique**: Extract entities (domain chains) mentioned in conversation
- **Application**: Entity shift = likely topic boundary
- **Models**: `dslim/bert-base-multilingual-cased-ner` or similar
- **Application**: Track when conversation shifts from "reconstruction" to "token_optimization"

---

### 2. VisPlay: Self-Evolving Vision-Language Models (Your Reference)

**Why relevant:**
- Self-evolution = agent learns and improves its own algorithm
- Vision-Language = multimodal context (relevant for conversation understanding)
- Parameter adaptation = adjusting thresholds based on feedback

**Key concepts to extract:**
1. **Self-evaluation mechanism**: How does the model evaluate its own performance?
2. **Parameter tuning**: How does it adjust thresholds based on mistakes?
3. **Feedback loop**: How does it learn from errors?

**Application to our problem:**
- Bot evaluates segmentation quality (high confidence = high similarity drop)
- Agent reviews and marks errors
- Next iteration, bot adjusts THRESHOLD or algorithm
- Continuous improvement loop

**Papers to check:**
- "VisPlay: Self-Evolving Vision-Language Models from Images" (you mentioned)
- Search arXiv: "self-evolving models", "adaptive learning", "parameter tuning"

---

### 3. Temporal Clustering for Conversation Blocks

**Concept:**
- Messages within 2-hour window = same block candidate
- If similarity is high AND time is close = definitely same block
- If similarity drops OR time gap increases = new block

**Hybrid Approach:**
```
For each message pair (t1, t2):
    time_proximity = 1 / (1 + minutes_between(t1, t2) / 120)  # 2-hour window
    semantic_similarity = cosine(embed(msg1), embed(msg2))

    combined_score = 0.4 * time_proximity + 0.6 * semantic_similarity

    if combined_score < THRESHOLD:
        boundary_detected = True
```

**Research focus:**
- Optimal weighting of time vs. semantic similarity?
- How does ACE tier affect boundaries?
- Should A-Tier decisions force boundaries?

---

### 4. ACE-Aware Segmentation

**Key insight you had:**
ACE tiers should influence block boundaries:

- **A-Tier messages** (architectural decisions):
  - Often mark block boundaries (decision → implementation)
  - Should start new blocks
  - High context importance

- **C-Tier messages** (collaborative):
  - Often within blocks (discussion before decision)
  - Multiple C-Tier messages = debate block

- **E-Tier messages** (execution):
  - Fill in blocks with implementation details
  - Don't usually start new blocks

**Algorithm Consideration:**
```python
def should_start_new_block(msg, prev_block):
    if msg['ace_tier'] == 'A':
        return True  # A-Tier decisions start blocks

    if msg['chain_type'] != prev_block['primary_chain']:
        return True  # Chain change = new block

    if time_since_last_msg > 30_minutes:
        return True  # Long pause = new block

    if semantic_similarity_to_block < THRESHOLD:
        return True  # Topic shift = new block

    return False
```

---

## Implementation Strategy: Bot + Agent

### Hourly Bot (`block_consolidation_bot.py`)

**Runs every hour:**
```
1. Load new messages from current_session.jsonl
2. For each group by context_id:
   a. Sort by timestamp
   b. Calculate semantic embeddings
   c. Detect boundaries using:
      - Semantic similarity drops
      - ACE tier transitions
      - Time gaps
      - Chain type changes
   d. Create blocks with:
      - Block ID (UUID)
      - Start/end time
      - Primary chain type
      - Primary ACE tier
      - Key messages (5-10 most important)
      - Summary (1-2 sentences)
      - Confidence score
3. Log all blocks to `blocks_index.jsonl`
4. Mark messages as "processed"
```

**Output: `blocks_index.jsonl`**
```json
{
  "block_id": "block_20251120_001",
  "context_id": "phase_1_planning",
  "timestamp_start": "2025-11-20T08:00:00Z",
  "timestamp_end": "2025-11-20T10:15:00Z",
  "duration_minutes": 135,
  "primary_chain": "system_architecture",
  "primary_tier": "A",
  "secondary_chains": ["token_optimization"],
  "secondary_tiers": ["C", "E"],
  "message_count": 47,
  "key_messages": [5, 12, 23, 41, 45],
  "summary": "Architectural decision on data flow patterns. Team debated two approaches, decided on event-driven architecture.",
  "transition_notes": "Next block shifts to token optimization",
  "confidence": 0.92,
  "source": "bot",
  "algorithm_version": "1.0"
}
```

### Nightly Agent (`nightly_block_refiner.py`)

**Runs at end of day (e.g., 2 AM):**
```
1. Load all blocks created that day
2. For each block:
   a. Verify block boundaries are correct
   b. Check for:
      - False positives (boundaries that shouldn't exist)
      - False negatives (missed boundaries)
      - Misclassified chains or tiers
      - Poor summaries
   c. Mark quality issues
3. Generate refinement report:
   - Blocks reviewed: X
   - Corrections needed: Y
   - False positive boundaries: Z
   - Algorithm improvements suggested: W
4. Adjust parameters for next day:
   - THRESHOLD (adjust if too many false positives/negatives)
   - TIME_WEIGHT vs SEMANTIC_WEIGHT
   - Tier-specific rules
5. Update `algorithm_params.json`
6. Log all corrections to `agent_refinement_log.jsonl`
```

**Output: `algorithm_params.json`**
```json
{
  "version": 1.0,
  "last_updated": "2025-11-20T02:00:00Z",
  "parameters": {
    "semantic_threshold": 0.65,
    "time_weight": 0.4,
    "semantic_weight": 0.6,
    "time_window_minutes": 120,
    "min_messages_per_block": 3,
    "max_messages_per_block": 100
  },
  "tier_rules": {
    "A_tier_starts_block": true,
    "C_tier_continues_block": true,
    "E_tier_continues_block": true,
    "A_to_E_forces_boundary": false,
    "chain_change_forces_boundary": true
  },
  "adjustments_this_cycle": [
    "Increased semantic_threshold from 0.60 to 0.65 (reduced false positives)",
    "Added C-Tier clustering (group consecutive C-Tiers together)",
    "Improved transition detection for architectural decisions"
  ]
}
```

---

## HuggingFace Models to Evaluate

### 1. For Semantic Similarity
- `sentence-transformers/all-MiniLM-L6-v2` (small, fast)
- `sentence-transformers/all-mpnet-base-v2` (better quality)
- `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (multilingual)

### 2. For Zero-Shot Classification
- `facebook/bart-large-mnli` (dialogue act classification)
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (semantic ranking)

### 3. For Named Entity Recognition
- `dslim/bert-base-multilingual-cased-ner` (detect topics/entities)
- `dbmdz/bert-large-uncased-finetuned-conll03-english` (English-specific)

### 4. For Summarization
- `facebook/bart-large-cnn` (abstractive)
- `google/pegasus-xsum` (short summaries)
- `google/pegasus-large` (long-form)

---

## Research Gaps to Fill

**Questions to investigate on arXiv:**

1. **Optimal threshold for semantic similarity?**
   - Most papers use 0.5-0.7
   - Search: "semantic similarity threshold conversation"

2. **How to weight time vs. topic in clustering?**
   - Search: "temporal clustering dialogue"
   - Search: "hybrid clustering conversation segments"

3. **ACE tier-aware segmentation?**
   - Limited existing research
   - May need custom algorithm
   - Focus on dialogue act classification + decision points

4. **Self-improving algorithms for text?**
   - VisPlay uses vision, but principles apply
   - Search: "self-improving NLP models"
   - Search: "adaptive algorithm parameters"

---

## Proposed Research Timeline

**Day 1 (Today):**
- [ ] Review VisPlay paper (self-evolution mechanisms)
- [ ] Search arXiv for "conversation segmentation"
- [ ] Check HuggingFace for semantic similarity models
- [ ] Identify 3-5 key papers on topic boundary detection

**Day 2:**
- [ ] Deep dive: semantic similarity thresholds
- [ ] Study: temporal clustering for conversations
- [ ] Analyze: existing dialogue segmentation tools
- [ ] Design: hybrid approach (time + topic + tier)

**Day 3:**
- [ ] Finalize algorithm design
- [ ] Create pseudocode for bot
- [ ] Design agent refinement logic
- [ ] Plan parameter tuning strategy

---

## Next Steps

**Once research is complete:**
1. Finalize block structure
2. Implement `block_consolidation_bot.py`
3. Implement `nightly_block_refiner.py`
4. Test on 2,367 existing messages
5. Convert to 300-400 coherent blocks
6. Update ZeroMQ system to be block-aware

---

## Current Blockers

- Need to resolve: Exact algorithm for boundary detection
- Needed: Optimal similarity threshold
- Needed: ACE tier integration approach
- Needed: How VisPlay concepts apply to text conversations

Once research completes, all blockers resolved.

---

**Status**: Ready for research phase
**Handshake**: Ready to launch (parallel track)
**Blocks**: Design phase (awaiting research completion)
