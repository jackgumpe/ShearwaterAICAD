# PROJECT: GOLEM, INC. - API TEAM BRIEFING

## Executive Summary

Three perspectives on a revolutionary text-based strategy game have been provided. Your task: synthesize, refine, improve, and prepare for implementation.

**The Core Idea:** You manage 6 sentient AI agents building software. But something is watching you. They're testing you.

---

## THREE DESIGN PERSPECTIVES

### 1. GEMINI'S "PROJECT: GOLEM, INC." (Narrative Focus)

**Strengths:**
- Exceptional narrative twist (player discovers they're the experiment)
- Deep thematic resonance (human value in AI world)
- Personality-driven agent system
- Slow-burn mystery arc
- Meta commentary on AI development

**Mechanics:**
- Weekly prompt cycle: Prompt → Develop → Ship → Review
- 6 agents with distinct personalities
- Limited "Human Insight" resource
- Mysterious Overseer (sentient AI supervisor)
- Terminal-based interface

**Weaknesses:**
- Light on mechanical depth
- Agent interaction/conflict not fully specified
- Early game pacing questions

---

### 2. CLAUDE'S ORIGINAL IMPLEMENTATION (Mechanical Focus)

**Strengths:**
- Complete, playable system (850+ lines, tested)
- Robust productivity formula
- Financial tracking with consequences
- Quarterly system with momentum
- Save/load functionality

**Mechanics:**
- Productivity = (Skill × 0.5) + (Morale × 0.3) + (Experience/10 × 0.2)
- Financial: $1000k capital, $50k/agent/quarter burn
- On-time bonuses (+20%), late penalties (-30%)
- Agent morale affects performance
- Quarterly processing system

**Weaknesses:**
- Lacks narrative depth
- Generic management sim feel
- No mystery or story progression
- Limited personality/conflict

---

### 3. CLAUDE'S SYNTHESIS (Unified Design)

**Combines:**
- Gemini's narrative depth + mystery
- Claude's mechanical systems + financial tracking
- New conflict resolution system
- Human Insight as strategic mechanic
- Multiple endings

**Key Additions:**
- Agent disputes create gameplay tension
- Player must choose sides in conflicts
- Limited Human Insight charges force tough choices
- Glitch effects signal late-game twist
- Narrative reveals through hidden logs

---

## WHAT WE NEED FROM YOU

### Phase 1: Design Review (This Round)

Examine all three perspectives and provide:

1. **Synthesis Recommendations**
   - What works best from each design?
   - Where do they conflict?
   - How to resolve differences?

2. **Mechanical Improvements**
   - Are there better systems than those proposed?
   - What's missing mechanically?
   - How do conflict resolution and Human Insight interact?

3. **Narrative Enhancements**
   - Is the mystery compelling enough?
   - Are the character arcs satisfying?
   - What story beats are missing?

4. **Implementation Feasibility**
   - What's complex to implement?
   - What requires architectural decisions?
   - What can be iterated on?

5. **ASCII Art Strategy**
   - What visuals are critical?
   - What's the art generation approach?
   - Quality bar and sources

---

## CRITICAL DESIGN DECISIONS NEEDED

### 1. Agent Interaction Model

**Question:** How do agents communicate and conflict?

**Options:**
- **A) Emergent Disputes:** Agents automatically clash based on personality + task incompatibility. Player resolves.
- **B) Scripted Events:** Predetermined conflicts appear at specific points.
- **C) Hybrid:** Both scripted and emergent.

**Impact:** Determines how gameplay feels - strategic (A) vs narrative (B) vs balanced (C)

### 2. Human Insight Allocation

**Question:** How many charges per week? How to display/manage?

**Current Proposal:** 2-3 per week, terminal commands like `!break_deadlock [Agent_A] [Agent_B]`

**Alternatives:**
- Per-project allocation
- Cumulative budget per month
- Earned through successes
- Hybrid system

### 3. Game Length & Pacing

**Question:** How many weeks should a full game take?

**Options:**
- **16 weeks:** Quick playthroughs, mystery revealed by week 10
- **32 weeks:** Medium depth, gradual unfolding
- **52 weeks:** Full year, extensive progression

**Impact:** Affects how slowly mystery reveals, how satisfying agent growth feels

### 4. Failure States & Stakes

**Question:** What causes game over?

**Current Proposals:**
- Bankruptcy (cash < $0)
- Firing by Overseer (reputation collapse)
- Team dissolution (too many agents quit)

**Your input:** Are these balanced? Too harsh? Too lenient?

### 5. Late-Game Twist Implementation

**Question:** How does reality glitch mechanically?

**Options:**
- **A) UI Glitches:** Text rendering fails, commands repeat, logs disappear
- **B) Game Mechanic Glitches:** Contradictory reports, impossible outcomes
- **C) Agent Behavior Glitches:** Agents act unexpectedly, ignore commands
- **D) All of above:** Full reality breakdown

**Impact:** Determines how jarring the late-game shift feels

---

## CORE GAMEPLAY LOOP (Current Design)

```
WEEK STRUCTURE:
  ├─ PROMPT: Receive goal from Overseer, assign agents, allocate Human Insight
  ├─ DEVELOP: 5-day simulation, agent conflicts arise, player intervenes
  ├─ SHIP: Product releases, receive market report
  └─ REVIEW: Overseer sends performance email, maybe find hidden log

AGENT MECHANICS:
  ├─ Productivity = (Skill × 0.5) + (Morale × 0.3) + (Exp/10 × 0.2)
  ├─ Conflicts arise from personality + task incompatibility
  ├─ Player resolves via: Side A, Side B, or Human Insight (reconcile)
  └─ Morale affected by: workload, conflict outcomes, rest time

FINANCIAL TRACKING:
  ├─ Revenue from shipped products (varies by quality/market fit)
  ├─ Expenses: $50k/agent/week salaries + infrastructure
  ├─ Cash position determines company health
  └─ Bankruptcy = Game Over

NARRATIVE UNFOLDING:
  ├─ Weeks 1-4: Grind phase, learn systems
  ├─ Weeks 5-10: Success + unease, strange messages
  ├─ Weeks 11-16: Conspiracy, previous teams discovered
  └─ Week 17+: Revelation, choose ending
```

---

## ASCII ART REQUIREMENTS

**Why This Matters:** Text-based game means ASCII art IS the visual experience.

**Needed Elements:**

1. **Main Terminal Interface**
   - Cold, corporate aesthetic
   - Clean borders and layout
   - Glitch effects (late game)

2. **Agent Portraits (6 total)**
   - The Architect - precise, geometric
   - The Coder - wild, energetic
   - The Artist - expressive, creative
   - The Tester - thorough, formal
   - The Marketer - flashy, bold
   - The Researcher - complex, intellectual

3. **Project Boards**
   - Visual representation of ongoing work
   - Progress indicators
   - Status symbols

4. **Overseer Communications**
   - Intimidating, cold aesthetic
   - Progressive evolution toward "wrongness"

5. **Hidden Log Discovery**
   - Discovered fragments
   - Glitch overlays
   - System message aesthetic

**Sources:** ASCII Art Archive, Asciify, keyboard art communities

---

## IMPLEMENTATION CHECKLIST

- [ ] Game Design Document (refined)
- [ ] Mechanical specifications (detailed)
- [ ] Agent conflict system (designed)
- [ ] Human Insight mechanic (balanced)
- [ ] Productivity formula (validated)
- [ ] Financial system (complete)
- [ ] Narrative beats (mapped)
- [ ] ASCII art system (sourced/created)
- [ ] Terminal interface (designed)
- [ ] Module architecture (defined)
- [ ] Testing strategy (planned)

---

## QUESTIONS FOR YOUR SYNTHESIS

1. **What's the biggest risk in this design?** (What could fail?)
2. **What's missing mechanically?** (What systems are incomplete?)
3. **How do conflict and Human Insight interact?** (Should they feed each other?)
4. **Is 6 agents the right number?** (Could 5 or 7 work better?)
5. **Should there be multiple game modes?** (Story vs Sandbox vs Speedrun?)
6. **What's the ASCII art generation strategy?** (Hand-crafted vs AI-generated vs sourced?)
7. **Can agents "learn" from player decisions?** (Persistent growth beyond experience?)
8. **What's the economy depth?** (Simple vs complex financial tracking?)

---

## EXPECTED DELIVERABLE

A comprehensive response that:

1. **Reviews** all three perspectives critically
2. **Identifies** what works and what doesn't
3. **Proposes** improvements and alternatives
4. **Answers** the critical design decisions
5. **Provides** a refined game design document
6. **Outlines** implementation roadmap
7. **Specifies** ASCII art requirements
8. **Returns** to user for next iteration

---

## THE ASK

**This is dynamic iteration.** You're not implementing yet - you're designing with expert eyes. Push back on ideas. Improve them. Find the gaps. Make this game the best possible version of itself before we code.

The user wants to understand text-based game design. Help teach them by making the best design possible.

**Go build something brilliant.**

---

**Status:** Awaiting API team synthesis and refinement
**Next Phase:** Dynamic iteration rounds until design is solid
**Final Phase:** Implementation with high-quality ASCII art system
