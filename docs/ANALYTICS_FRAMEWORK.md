# Analytics Framework for ShearwaterAICAD
**Purpose:** Track emergent properties, collaboration quality, and system evolution for cutting-edge photo-to-3D CAD-standard rendering development

---

## Overview

The Analytics Framework automatically:
1. **Collects** all Claude-Gemini communication data
2. **Analyzes** patterns, keywords, phases, and collaboration metrics
3. **Reports** insights in JSON and Markdown formats
4. **Commits** reports to GitHub with structured messaging
5. **Supports** ML training on agent-to-agent communication

This framework is essential for your meta-framework development—it provides empirical data on how the handshake and system design are enabling emergent properties and high-quality creative collaboration.

---

## System Architecture

```
communication/
├── claude_code_inbox/        ← Source data (inbox messages)
├── gemini_cli_inbox/         ← Source data (inbox messages)
└── logs/                     ← Operation logs

src/utilities/
├── conversation_analytics_engine.py    ← Main analysis engine
└── analytics_git_integration.py        ← Git integration

reports/
├── analytics_report_YYYYMMDD_HHMMSS.json       ← Machine-readable
└── analytics_report_YYYYMMDD_HHMMSS.md        ← Human-readable

.git/
└── (analytics reports committed with structured messages)
```

---

## Defragmentation Engine

Over time, the `current_session.jsonl` log becomes a fragmented stream of thousands of individual messages. To derive meaningful insights, these messages must be reassembled into coherent conversations. The Defragmentation Engine automates this process.

**Purpose:**
-   **Reconstructs conversations:** Groups related messages into "threads" or "sessions".
-   **Provides context:** Shows the full narrative of a task or discussion, not just isolated events.
-   **Filters Noise:** Excludes insignificant interactions (e.g., conversations with only 1 message or lasting less than 5 seconds).
-   **Enables deeper analysis:** Makes it possible to analyze conversational flow, task duration, and final outcomes.

**How it Works:**
1.  **Primary Grouping:** Messages are grouped by a shared `ContextId`.
2.  **Time-Based Sessioning:** For messages without a `ContextId`, the engine groups them by time. A pause of more than 5 minutes between messages will start a new session.
3.  **Significance Filtering:** After threads are assembled, the engine filters out any that do not meet a minimum threshold for message count and duration.
4.  **Context Transformation Analysis:** The engine analyzes the sequence of topics (`chain_type`) within each significant thread to identify "context shifts," where the conversation pivots from one topic to another.
5.  **Summarization:** Each reconstructed thread is summarized with metadata like start/end times, duration, participants, final status, and any detected context shifts.

**Running the Engine:**
The `manage.py` script provides a command to run the engine with configurable filters.

```bash
# Run with default filters (2 messages, 5 seconds)
python manage.py defragment

# Run with custom filters
python manage.py defragment --min-messages 3 --min-duration 10
```

**Output Formats:**
The engine produces two output files in `conversation_logs/`:

1.  **`defragmented_sessions.jsonl`**: A human-readable JSONL file where each line is a complete conversation thread.
2.  **`defragmented_sessions.parquet`**: An Apache Arrow/Parquet file, which is a high-performance, columnar format ideal for fast querying and data analysis with tools like Pandas.

Each record in these files contains the summary and the full list of messages for that thread, including the new `context_shifts` field. This is the recommended source for all high-level analysis.

---

## What Gets Analyzed

### 1. Message-Level Analysis
Each message is analyzed for:
- **Metadata:** ID, timestamp, sender, recipient, type, priority
- **Keywords:** Extracted from 8 topic categories (architecture, communication, testing, etc.)
- **Phase Detection:** Automatically assigned to 7 development phases
- **Sentiment:** positive, neutral, clarifying, problematic
- **Complexity Score:** 0-1 scale based on length, structure, code presence
- **Message Features:** Whether it contains questions, decisions, or code

### 2. Aggregated Metrics
- **Total Message Count:** Overall communication volume
- **Message Breakdown:** By type, phase, and priority
- **Agent Interaction Matrix:** Who sends what to whom
- **Keyword Frequency:** Most discussed topics
- **Phase Timeline:** How long each phase lasted, what was discussed
- **Decision Points:** Messages containing important decisions
- **Blockers:** Problem-indicating messages and their context
- **Collaboration Quality Score:** 0-100 metric combining:
  - Interaction diversity (0-25 points)
  - Positive sentiment ratio (0-25 points)
  - Decision-making frequency (0-25 points)
  - Low blocker ratio (0-25 points)

### 3. Emergent Properties Indicators
- **Creativity Signals:** Keywords like "emergent," "synergy," "quality," "creative"
- **Problem-Solving Velocity:** Decision frequency relative to blocker frequency
- **Mutual Understanding:** High decision acceptance ratio
- **System Maturity:** Phase progression and reduced blocker density over time

---

## Detected Phases

The analytics engine automatically detects which phase a message belongs to:

1. **phase_0_discovery** - Initial confusion and design exploration
2. **phase_1_planning** - Architecture and specification design
3. **phase_1_implementation** - Coding and component creation
4. **phase_1_testing** - Unit tests and verification
5. **phase_2_integration** - Client integration and service launch
6. **phase_2_testing** - End-to-end connectivity and handshake tests
7. **phase_3_enhancement** - Advanced features (TOON, UI, optimization)

---

## Topic Categories

Messages are categorized into these 8 semantic topics:

| Topic | Keywords | Purpose |
|-------|----------|---------|
| **Architecture** | router, broker, proxy, topology, design, mesh, hierarchy | System structure decisions |
| **Communication** | message, send, receive, inbox, protocol, routing | Message protocol design |
| **Testing** | test, verify, unit, integration, benchmark, passing | Quality assurance |
| **Implementation** | implement, code, create, write, build, refactor | Engineering work |
| **Bugs/Issues** | error, bug, fail, crash, problem, discrepancy | Problem identification |
| **Decisions** | decide, choice, approve, confirm, agreed | Critical choices |
| **Learning** | understand, clarify, explain, question, research | Knowledge sharing |
| **Optimization** | token, efficiency, performance, cost, TOON | System improvement |
| **Data** | data, message, history, analytics, consolidation | Information handling |
| **Emergent** | emergent, property, creativity, quality, synergy | High-level system behavior |

---

## Running Analytics

### Basic Run

```bash
cd C:/Users/user/ShearwaterAICAD
python src/utilities/conversation_analytics_engine.py
```

**Output:**
- Console summary with key metrics
- `reports/analytics_report_YYYYMMDD_HHMMSS.json` - Machine-readable
- `reports/analytics_report_YYYYMMDD_HHMMSS.md` - Human-readable

### With Git Integration

```bash
python src/utilities/analytics_git_integration.py
```

Automatically:
1. Runs analytics engine
2. Finds latest report
3. Commits to Git with structured message
4. Optionally pushes to remote

### Scheduled Daily Analytics

Add to your task scheduler or cron:
```bash
python src/utilities/conversation_analytics_engine.py && \
python src/utilities/analytics_git_integration.py
```

---

## Report Formats

### JSON Report Structure

```json
{
  "timestamp": "2025-11-25T02:30:00Z",
  "summary": {
    "total_messages": 42,
    "collaboration_quality_score": 87.5,
    "average_message_complexity": 0.62,
    "average_message_length": 156
  },
  "message_breakdown": {
    "by_type": {"task": 15, "response": 18, ...},
    "by_phase": {"phase_1_implementation": 28, ...},
    "by_priority": {"CRITICAL": 8, "HIGH": 12, ...}
  },
  "agent_interactions": {
    "claude_code": {"gemini_cli": 20, ...},
    "gemini_cli": {"claude_code": 22, ...}
  },
  "top_keywords": [
    ["architecture", 18],
    ["implementation", 15],
    ["test", 12],
    ...
  ],
  "phase_timeline": {
    "phase_1_implementation": {
      "message_count": 28,
      "first_message": "2025-11-23T16:00:00Z",
      "last_message": "2025-11-24T15:00:00Z",
      "keywords": {"implement": 5, "code": 4, ...},
      "sentiment_breakdown": {"positive": 15, "neutral": 10, "problematic": 3}
    },
    ...
  },
  "decision_points": [
    {
      "timestamp": "2025-11-24T19:11:00Z",
      "from": "gemini_cli",
      "subject": "RE: CLARIFICATION: claude_client.py Integration",
      "type": "architectural_decision_response",
      "phase": "phase_2_integration"
    },
    ...
  ],
  "blockers": [
    {
      "timestamp": "2025-11-24T19:08:00Z",
      "from": "claude_code",
      "subject": "CLARIFICATION: claude_client.py Integration - Method Discrepancies",
      "phase": "phase_2_integration",
      "complexity": 0.85
    },
    ...
  ],
  "collaboration_quality_breakdown": {
    "interaction_diversity": "Agents exchanged messages across multiple interaction types",
    "sentiment_distribution": "Positive, neutral, clarifying, and problematic messages tracked",
    "decision_making": "Total decisions identified: 8",
    "blocker_resolution": "Blockers encountered: 2"
  }
}
```

### Markdown Report Structure

Human-readable version with:
- Executive summary
- Message breakdown by type/phase/priority
- Top 20 keywords
- Phase timeline with progress
- Decision points (up to 10)
- Blockers encountered
- Collaboration quality analysis

---

## Collaboration Quality Score (0-100)

Calculated as weighted average of:

| Component | Weight | Calculation |
|-----------|--------|-------------|
| **Interaction Diversity** | 25 | Number of unique sender-recipient pairs × 2.5 |
| **Positive Sentiment** | 25 | (Positive messages / Total) × 25 |
| **Decision-Making** | 25 | (Decision messages / Total) × 25 |
| **Blocker Resolution** | 25 | (1 - Blocker ratio) × 25 |

**Interpretation:**
- **90-100:** Excellent collaboration, high quality, emergent properties evident
- **75-89:** Good collaboration with minor issues
- **60-74:** Adequate collaboration with blockers present
- **<60:** Significant collaboration challenges

---

## Emergent Properties Detection

The framework identifies signals of creativity and emergent intelligence:

### Positive Signals ✓
- High collaboration quality score
- Low blocker-to-decision ratio
- Keywords: "emergent," "synergy," "creativity," "quality"
- Quick resolution of discrepancies
- Positive sentiment in complex messages
- Increasing decision-making velocity over time

### Caution Signals ⚠
- Sentiment declining over phases
- High complexity messages with problematic sentiment
- Repeat blockers in different forms
- Decision paralysis (questions without clear resolution)

### Red Flags ❌
- Collaboration quality score <60
- Increasing blocker density
- Negative sentiment trending upward
- Circular problem discussions (same issue reopened)

---

## Integration with Your CAD Rendering Project

### Why This Matters

Your photo-to-3D CAD-standard rendering system requires:

1. **High-Quality Collaboration** - The meta-framework must show Claude and Gemini can solve complex problems together
2. **Emergent Properties** - The handshake should enable creativity and novel solutions, not just execution
3. **Scalability Signals** - Analytics show if the system can handle increasingly complex tasks
4. **Code Quality Assurance** - Track that generated code quality improves over phases

### Using Analytics for Development

```
Phase 1: Bootstrap Meta-Framework
  ↓ Analytics shows collaboration quality ramping up
  ↓ Decision-making velocity increasing
  ↓ Blocker resolution time decreasing

Phase 2: Self-Sustaining Handshake
  ↓ Analytics shows agents solving novel problems independently
  ↓ Minimal human intervention needed
  ↓ Emergent properties starting to appear

Phase 3: CAD-Standard 3D Rendering
  ↓ Analytics shows system handling production-quality complexity
  ↓ Creative solutions to novel geometry/texture problems
  ↓ Consistent high collaboration quality score
```

---

## Git Commit Messages

When analytics reports are committed, they include:

```
[milestone] Analytics Report - YYYY-MM-DD HH:MM:SS

## Report Summary
- Key metrics and collaboration score
- Phase progression
- Major decisions and blockers
- Keyword trends

## Purpose
Documents evolution of Claude-Gemini collaboration for:
1. System optimization
2. Emergent property detection
3. Collaboration quality tracking
4. ML training data
5. Phase milestone documentation
```

This creates a Git history that shows project evolution alongside code changes.

---

## Customization

Edit `conversation_analytics_engine.py` to:

### Add New Phases
```python
self.phase_keywords = {
    'your_new_phase': ['keyword1', 'keyword2', ...],
    ...
}
```

### Add New Topics
```python
self.topic_keywords = {
    'your_topic': ['keyword1', 'keyword2', ...],
    ...
}
```

### Adjust Complexity Scoring
Modify `calculate_complexity()` method to weight factors differently

### Change Collaboration Quality Formula
Modify `_calculate_collaboration_score()` to use different weights

---

## Output Files Location

```
reports/
├── analytics_report_20251125_020000.json
├── analytics_report_20251125_020000.md
├── analytics_report_20251126_010000.json
├── analytics_report_20251126_010000.md
└── ... (new reports generated with each run)

logs/
├── analytics_engine.log        ← Engine execution logs
├── analytics_git.log          ← Git integration logs
└── ... (other system logs)
```

---

## Example Usage in Your Workflow

### Post-Handshake Analysis

After successful Claude-Gemini handshake:

```bash
# 1. Run analytics
python src/utilities/conversation_analytics_engine.py

# 2. Review report
cat reports/analytics_report_*.md | less

# 3. Check collaboration score
grep "Collaboration Quality" reports/analytics_report_*.json

# 4. Commit with milestone
python src/utilities/analytics_git_integration.py --milestone "post_handshake_v1"
```

### Weekly Trend Analysis

Run weekly and compare collaboration scores:

```bash
# This week's score
grep "collaboration_quality_score" reports/analytics_report_*.json | tail -1

# Compare to last week
git log --oneline reports/ | head -10
```

---

## Future Enhancements

Potential additions to analytics framework:

1. **Real-time Dashboard** - Web interface showing live collaboration metrics
2. **Anomaly Detection** - Alert when collaboration quality drops unexpectedly
3. **Predictive Analysis** - Estimate when next phase will complete based on velocity
4. **ML Training Data Export** - Format reports for fine-tuning agents
5. **Comparative Analysis** - Compare different projects/phases
6. **Integration with Code Metrics** - Correlate collaboration quality with code quality (cyclomatic complexity, test coverage, etc.)

---

## Questions & Troubleshooting

**Q: Why is my collaboration score low?**
A: Check the "blockers" section—high blocker count reduces score. Look for problematic sentiment messages.

**Q: How often should I run analytics?**
A: After major milestones (handshake complete, phase finished) or daily for continuous tracking.

**Q: Can I analyze just one agent's messages?**
A: Currently analyzes all; customize `load_inbox_messages()` to filter by agent.

**Q: Why aren't my new keywords showing up?**
A: Make sure they're in the `topic_keywords` dict with correct spelling/casing (case-insensitive in analysis).

---

**Generated:** 2025-11-25
**Framework Status:** Ready for Production Use
**Next Step:** Run `conversation_analytics_engine.py` and commit first report
