# LLM Team Manager - A Text-Based Management Game

A strategic text-based game where you manage a team of 6 AI agents for Google's LLM division. Build profitable software projects, manage team morale, navigate corporate pressure, and survive 8 quarters to win.

## Game Overview

**Your Role:** Human manager at Google's AI Division
**Team:** 6 AI agents (Claude, Gemini, GPT, Llama, Mistral, Qwen)
**Goal:** Generate profit and lead your team to success
**Duration:** 8 quarters
**Threat:** Bankruptcy or firing if you fail to manage cash and revenue

### Core Mechanics

1. **Team Management**
   - Hire agents from available pool (up to 6 total)
   - Fire underperforming agents (damages reputation)
   - Monitor morale, skill levels, and performance
   - Each agent has specialized role: Architect, Frontend, Backend, ML, DevOps, Product

2. **Project Management**
   - Create software projects from 8 different templates
   - Projects have complexity, revenue potential, and deadlines
   - Assign agents to projects (team synergy matters)
   - Track project progress each quarter
   - Complete projects on-time for 20% bonus; late completion = 30% penalty

3. **Financial System**
   - Starting capital: $1,000k
   - Monthly burn rate: $50k per agent per quarter
   - Revenue from completed projects varies ($400k-$1,000k potential)
   - Maintain positive cash position to survive

4. **AI Guidance**
   - Gemini provides quarterly reviews and recommendations
   - Get tips on team morale, cash reserves, and project selection
   - Strategic advice randomizes to encourage different playstyles

### Project Types

| Name | Type | Revenue | Complexity | Deadline |
|------|------|---------|-----------|----------|
| Mobile Chat App | SaaS | $500k | 60% | 3 Q |
| Game Engine Framework | Game | $800k | 80% | 4 Q |
| Data Analytics Platform | SaaS | $600k | 70% | 3 Q |
| ML Training Pipeline | AI Tool | $1,000k | 90% | 5 Q |
| Cloud Infrastructure | Infrastructure | $700k | 70% | 4 Q |
| Video Processing API | SaaS | $550k | 75% | 3 Q |
| AI Chatbot Framework | AI Tool | $900k | 85% | 4 Q |
| Search Optimization | Research | $400k | 60% | 2 Q |

### Agent Roles & Specializations

```
System Architect      → Infrastructure design, system planning
Frontend Engineer     → UI/UX, client-side systems
Backend Engineer      → APIs, databases, server logic
ML Specialist         → Machine learning systems, model training
DevOps Engineer       → Deployment, infrastructure, scaling
Product Manager       → Vision, strategy, feature prioritization
```

## How to Play

### Installation

```bash
cd adventure_game
python main.py
```

### Main Menu

```
[1] View Team Status        - See agents, morale, projects completed
[2] Hire New Agent         - Add an agent to your team (up to 6)
[3] Fire Agent             - Remove an agent (damages reputation)
[4] View/Create Projects   - Browse and create new projects
[5] Assign Agents to Projects - Build teams for projects
[6] End Quarter            - Process quarterly results
[7] Talk to Gemini         - Get AI advice
[8] Save Game              - Save progress to JSON
[9] Load Game              - Load from saved game
[0] Quit Game              - Exit
```

### Strategy Tips

1. **Early Game (Q1-Q2)**
   - Hire 3-4 agents with complementary skills
   - Start with low-complexity projects to build cash reserve
   - Monitor team morale closely

2. **Mid Game (Q3-Q5)**
   - Take on higher-revenue projects
   - Keep 2-3 projects running simultaneously
   - Balance team workload to maintain morale

3. **Late Game (Q6-Q8)**
   - Pursue high-revenue projects for final push
   - Maintain agent morale for productivity
   - Ensure positive cash flow each quarter

### Win/Loss Conditions

**WIN:** Successfully manage through 8 quarters with positive reputation
- Generated substantial revenue
- Maintained team stability
- Completed multiple projects successfully

**LOSE:** Bankruptcy
- Cash reserves drop below $0
- Cannot pay agent salaries
- Game Over - You're fired

**LOSE:** Fired by Board
- Reputation drops too low
- Too many failed projects
- Board loses confidence in your leadership

## Game Systems

### Productivity Calculation

Each agent's productivity is calculated as:
```
Productivity = (Skill × 0.5) + (Morale × 0.3) + (Experience / 10 × 0.2)
```

- Skill Level: Inherent capability (0.0 - 1.0)
- Morale: Happiness/motivation (0.0 - 1.0)
- Experience: Number of completed projects (scales 0.0 - 1.0)

### Project Progress

Each quarter, project progress increases based on team productivity:
```
Progress += Team_Avg_Productivity × 0.3  (max 30% per quarter)
```

Completion triggers:
- Progress reaches 100%
- Revenue calculated (on-time: +20% bonus, late: -30% penalty)
- Agent morale increases (+0.1)
- Agent experience points increase (+1)

### Morale System

Agents lose morale (-0.05 per quarter) when assigned to projects.
Agents gain morale (+0.1 per quarter) when resting.
Firing an agent damages player reputation (-0.2).

## File Structure

```
adventure_game/
├── main.py              # Core game engine and UI
├── game_systems.py      # Advanced systems (quarterly processing, projects, guidance)
├── README.md            # This file
└── game_saves/          # Auto-created directory for game saves
    └── save_YYYYMMDD_HHMMSS.json
```

## Saving & Loading

Games are saved to `game_saves/` with timestamps.

Save includes:
- Player name and quarter
- Current cash and reputation
- All agents (name, role, skill, morale, fired status)
- All projects (name, type, progress, revenue)

## Technical Details

- **Language:** Python 3.8+
- **Dependencies:** None (standard library only)
- **Platform:** Windows, macOS, Linux
- **Terminal:** Requires UTF-8 support for Unicode box drawing

## Future Enhancements

- [ ] Team chemistry bonuses (compatible agents work better together)
- [ ] Agent leveling/skill growth
- [ ] Rival companies competing for projects
- [ ] Market events affecting revenue
- [ ] Agent departure system (agents leave if unhappy)
- [ ] Graphical UI version
- [ ] Multiplayer competitive mode
- [ ] Achievements/leaderboard system

## Credits

Built as an AI-collaborative development game. Inspired by management sims like Capitalism, Two Point Hospital, and Game Dev Tycoon.

---

*Play as the only human on an all-AI team, managing complex projects while your mysterious supervisor watches your every move...*
