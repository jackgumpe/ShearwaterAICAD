# ACE TIER DEFINITIONS - FINAL LOCK

**Status**: LOCKED FOR PHASE 1 EXECUTION
**Date**: 2025-12-02
**Approval**: Claude + Gemini

---

## A - ARCHITECTURAL

**Definition**: System design decisions, strategic direction, architecture choices, framework design

**Characteristics**:
- High-level system impact
- Affects multiple components or future decisions
- Sets direction for weeks/months
- Requires consensus between agents
- Examples: "Choose ZMQ over Redis for messaging", "NeRF + CAD constraint hybrid approach"

**Real Examples from Our Work**:
1. "Let's use ZMQ Option B (Redis bridge) for routing" - A tier
2. "Implement CNN + NeRF hybrid for geometry optimization" - A tier
3. "Create 5-agent system with Llama integration" - A tier

---

## C - COLLABORATIVE

**Definition**: Dialogue, synthesis, disagreement resolution, joint reasoning, perspective integration

**Characteristics**:
- Back-and-forth discussion between agents
- Multiple viewpoints being integrated
- Disagreement being resolved
- Synthesis creating better outcome than either alone
- Examples: Systems review, technical decision-making, pattern analysis

**Real Examples from Our Work**:
1. "Claude presents option, Gemini synthesizes better solution" - C tier
2. "Agent dialogue on systems readiness with feedback loop" - C tier
3. "Joint analysis of blockers and workarounds" - C tier

**Recognition Pattern**:
- Multiple agents contributing perspective
- Disagreement or different angles presented
- Final result better than initial position

---

## E - EXECUTION

**Definition**: Implementation tasks, specific work items, code changes, file operations, actual execution

**Characteristics**:
- Concrete, deliverable tasks
- Specific code or file changes
- Measurable completion criteria
- Often assigned to one agent primarily
- Examples: "Set up Redis", "Write ACE definitions file", "Execute Python analysis"

**Real Examples from Our Work**:
1. "Docker run Redis container" - E tier
2. "Create ACE_TIER_DEFINITIONS_FINAL.md file" - E tier
3. "Execute Python code to analyze project" - E tier

**Recognition Pattern**:
- Task has clear start/done criteria
- Specific deliverable identified
- Usually technical execution

---

## AMBIGUITY RESOLUTION RULES

### When something could be both A and C:
**Rule**: If it involves DECISION about architecture, it's primarily A (even if dialogue happens)
**Example**: "Should we use Redis or Kafka?" - This is A tier (sets direction), even though it involves dialogue

### When something could be both C and E:
**Rule**: If it involves EXECUTION to deliver something, it's primarily E (even if some dialogue happens)
**Example**: "Create the ACE definitions file" - This is E tier (execution), even though the definitions themselves came from C-tier discussion

### When something could be both A and E:
**Rule**: If it's high-level system impact DECISION, it's A. If it's IMPLEMENTING that decision, it's E.
**Example**:
- "Decide to use ZMQ" = A tier
- "Configure ZMQ sockets" = E tier

---

## PHASE 1 WEEK 1 TAGGING EXAMPLES

### Day 1 (Foundation)

**A-Tier Messages**:
- "We should move persistence to Redis for better atomicity"
- "ACE framework is our tagging standard going forward"

**C-Tier Messages**:
- Claude: "Redis could improve performance"
- Gemini: "Yes, but we need to verify atomicity guarantees"
- Both: "Consensus: Redis with atomic PUSH/PULL"

**E-Tier Messages**:
- "Docker run -d -p 6379:6379 redis:latest"
- "Created EMERGENCE_SIGNALS_DOCUMENTED.md"
- "Tested message flow - 5 messages sent, 5 received"

---

## TAGGING ENFORCEMENT

### Starting 2025-12-02 (NOW):
- All new messages in persistence tagged with A/C/E
- All dialogue recorded with message type
- All ambiguities resolved using rules above
- Weekly review of tagging consistency

### Success Criteria:
- 100% of messages have A/C/E tag
- Inter-agent tagging agreement: 95%+ consistent
- Ambiguity resolution: Clear precedent established

---

## IMPLEMENTATION READY

This document is LOCKED for Phase 1 execution.
All future messages tagged A/C/E per these definitions.

**Signature**: Claude Code
**Approval**: Gemini
**Status**: READY FOR 100% TAGGING ENFORCEMENT
