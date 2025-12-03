# Analytics Quick Start Guide

## Run Analytics Now

```bash
cd C:/Users/user/ShearwaterAICAD
python src/utilities/conversation_analytics_engine.py
```

**Results:**
- Console output with key metrics
- JSON report: `reports/analytics_report_*.json`
- Markdown report: `reports/analytics_report_*.md`

---

## What You'll See

### Collaboration Quality Score
- **0-100 metric** showing Claude-Gemini collaboration effectiveness
- Based on: interaction diversity, positive sentiment, decision-making, blocker resolution

### Message Breakdown
- By type (task, response, question, decision)
- By phase (discovery, planning, implementation, testing, integration)
- By priority (CRITICAL, HIGH, NORMAL, LOW)

### Top Keywords
- Most discussed topics
- Shows what the agents are focusing on
- Helps identify project hot spots

### Phase Timeline
- How long each phase lasted
- Key topics for each phase
- Sentiment distribution per phase

### Decision Points
- All critical decisions identified
- When they happened
- Which agent made them

### Blockers
- Problems encountered
- Complexity level
- Which phase they occurred in

---

## Commit to GitHub

After running analytics:

```bash
python src/utilities/analytics_git_integration.py
```

Automatically:
1. Finds latest report
2. Commits with structured message
3. Optionally pushes to remote

---

## Integration with Your Workflow

### After Handshake Success
```bash
python src/utilities/conversation_analytics_engine.py
python src/utilities/analytics_git_integration.py --milestone "post_handshake"
```

### Weekly Tracking
```bash
# Check latest collaboration score
grep "collaboration_quality_score" reports/analytics_report_*.json | tail -1

# Compare trends
git log --oneline reports/ | head -5
```

### Phase Completion
```bash
# Generate report with phase milestone
python src/utilities/analytics_git_integration.py --milestone "phase_1_complete"
```

---

## Key Metrics Reference

| Metric | Ideal | Acceptable | Concern |
|--------|-------|-----------|---------|
| Collaboration Score | 80+ | 70-79 | <70 |
| Positive Messages | >60% | 50-60% | <50% |
| Decision/Blocker Ratio | >2:1 | 1.5:1 | <1.5:1 |
| Messages Per Phase | Decreasing | Stable | Increasing |
| Complexity Score | 0.4-0.7 | Any | Consistently >0.8 |

---

## Files Created

| File | Purpose |
|------|---------|
| `src/utilities/conversation_analytics_engine.py` | Main analytics engine (500+ lines) |
| `src/utilities/analytics_git_integration.py` | Git integration (150+ lines) |
| `docs/ANALYTICS_FRAMEWORK.md` | Complete documentation |
| `reports/analytics_report_*.json` | Machine-readable reports |
| `reports/analytics_report_*.md` | Human-readable reports |

---

## For Your CAD Project

This analytics framework validates your meta-framework by showing:

1. **Collaboration Quality** - Can Claude and Gemini work together effectively?
2. **Emergent Properties** - Are they solving novel problems creatively?
3. **Self-Sustainability** - Does the handshake enable independent problem-solving?
4. **Scalability** - Can they handle increasingly complex tasks?

Track these metrics as you develop the photo-to-3D CAD-standard rendering system.

---

**Status:** Ready to use
**Next Step:** Run analytics and review first report
