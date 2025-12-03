#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Team Manager - A Text-Based Game
Player: Single human managing a team of 6 AI agents for Google's LLM division
Guide: Google's Gemini AI helping you navigate the corporate world
Boss: Unseen AI supervisor monitoring profit and productivity
"""

import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import json
from datetime import datetime
from pathlib import Path

# Fix encoding for Windows
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class AgentRole(Enum):
    ARCHITECT = "System Architect"
    FRONTEND = "Frontend Engineer"
    BACKEND = "Backend Engineer"
    ML_SPECIALIST = "ML Specialist"
    DEVOPS = "DevOps Engineer"
    PRODUCT = "Product Manager"


class ProjectType(Enum):
    GAME = "Game Development"
    SAAS = "SaaS Platform"
    AI_TOOL = "AI Tool"
    RESEARCH = "Research Project"
    INFRASTRUCTURE = "Infrastructure"


@dataclass
class Agent:
    """Represents an LLM AI agent on the team"""
    name: str
    role: AgentRole
    skill_level: float  # 0.0 to 1.0
    experience: int = 0  # Projects completed
    morale: float = 0.8
    specialization: str = ""
    projects_completed: int = 0
    is_fired: bool = False

    def get_productivity(self) -> float:
        """Calculate current productivity based on skill, morale, and experience"""
        return (self.skill_level * 0.5 + self.morale * 0.3 + min(self.experience / 10, 1.0) * 0.2)

    def get_status(self) -> str:
        status = "⚙️ ACTIVE" if not self.is_fired else "❌ FIRED"
        morale_bar = "█" * int(self.morale * 10) + "░" * (10 - int(self.morale * 10))
        skill_bar = "█" * int(self.skill_level * 10) + "░" * (10 - int(self.skill_level * 10))
        return f"{self.name} ({self.role.value}) {status}\n  Morale: {morale_bar} {self.morale:.1f}\n  Skill: {skill_bar} {self.skill_level:.1f}\n  Projects: {self.projects_completed}"


@dataclass
class Project:
    """Represents a software project the team is working on"""
    name: str
    project_type: ProjectType
    complexity: float  # 0.0 to 1.0
    revenue_potential: int  # Thousands
    deadline_quarters: int
    assigned_agents: List[Agent] = field(default_factory=list)
    progress: float = 0.0
    is_completed: bool = False
    completion_quarter: Optional[int] = None
    revenue_earned: int = 0

    def get_summary(self) -> str:
        agents_str = ", ".join([a.name for a in self.assigned_agents]) if self.assigned_agents else "Unassigned"
        status = "✅ COMPLETE" if self.is_completed else f"▓" * int(self.progress * 20) + "░" * (20 - int(self.progress * 20))
        return f"{self.name} ({self.project_type.value})\n  Status: {status}\n  Team: {agents_str}\n  Revenue: ${self.revenue_earned}k"


@dataclass
class GameState:
    """Core game state"""
    player_name: str
    quarter: int = 1
    cash: int = 1000  # Starting capital in thousands
    reputation: float = 0.5
    agents: List[Agent] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    available_agents_pool: List[Agent] = field(default_factory=list)
    fired_agents: List[Agent] = field(default_factory=list)
    game_over: bool = False
    game_won: bool = False

    def get_monthly_burn_rate(self) -> int:
        """Calculate monthly salary/operational costs"""
        active_agents = [a for a in self.agents if not a.is_fired]
        return len(active_agents) * 50  # 50k per agent per quarter

    def get_company_health(self) -> str:
        """Return status of company"""
        if self.cash < 0:
            return "BANKRUPT - GAME OVER"
        elif self.cash < 200:
            return "CRITICAL - Must generate revenue soon"
        elif self.cash < 500:
            return "WARNING - Low cash reserves"
        elif self.cash < 1000:
            return "STABLE - Operating normally"
        else:
            return "THRIVING - Strong position"


class GameEngine:
    """Main game loop and logic"""

    def __init__(self):
        self.state: Optional[GameState] = None
        self.save_path = Path("game_saves")
        self.save_path.mkdir(exist_ok=True)

    def start_new_game(self, player_name: str):
        """Initialize a new game"""
        self.state = GameState(player_name=player_name)
        self.create_initial_agent_pool()
        self.display_welcome()

    def create_initial_agent_pool(self):
        """Create initial pool of available agents to hire"""
        roles = [AgentRole.ARCHITECT, AgentRole.FRONTEND, AgentRole.BACKEND,
                 AgentRole.ML_SPECIALIST, AgentRole.DEVOPS, AgentRole.PRODUCT]

        agent_names = [
            "Claude", "Gemini", "GPT", "Llama", "Mistral", "Qwen",
            "Phi", "Falcon", "Bloom", "Cohere", "Palm", "Aleph"
        ]

        for i, role in enumerate(roles):
            agent = Agent(
                name=agent_names[i],
                role=role,
                skill_level=0.6 + (i * 0.05),
                specialization=f"Expert in {role.value}"
            )
            self.state.available_agents_pool.append(agent)

    def display_welcome(self):
        """Display welcome screen"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                  🤖 LLM TEAM MANAGER 🤖                       ║
║                                                                ║
║  You are a human manager at Google's AI Division.              ║
║  You have been hired to lead a team of 6 LLM agents.           ║
║  Your job: Build profitable software products.                 ║
║  Your fate: Determined by quarterly performance reviews.       ║
║                                                                ║
║  Gemini (Google's AI guide) will advise you.                   ║
║  A mysterious supervisor watches your every move...            ║
║                                                                ║
║  Fail to turn a profit? You get fired.                         ║
║  Lose all your cash? Bankruptcy.                               ║
║  Excel for 8 quarters? You win the game.                       ║
╚════════════════════════════════════════════════════════════════╝
        """)
        print(f"\nWelcome, {self.state.player_name}!")
        print(f"Starting capital: ${self.state.cash}k")
        print(f"Available agents to hire: {len(self.state.available_agents_pool)}")

    def display_main_menu(self):
        """Display main menu"""
        print(f"""
╔════════════════════════════════════════════════════════════════╗
║ QUARTER {self.state.quarter} - {self.state.player_name}'s Division        ║
║ Cash: ${self.state.cash}k | Reputation: {self.state.reputation:.1f}/5.0 | Status: {self.state.get_company_health()[:20]}║
╚════════════════════════════════════════════════════════════════╝

[1] View Team Status
[2] Hire New Agent
[3] Fire Agent
[4] View/Create Projects
[5] Assign Agents to Projects
[6] End Quarter (Process Results)
[7] Talk to Gemini (AI Guide)
[8] Save Game
[9] Load Game
[0] Quit Game

What do you do?
        """)

    def view_team_status(self):
        """Display current team status"""
        active_agents = [a for a in self.state.agents if not a.is_fired]

        print(f"\n{'='*60}")
        print(f"TEAM STATUS - Quarter {self.state.quarter}")
        print(f"{'='*60}\n")

        if not active_agents:
            print("❌ You have no active agents! Hire someone to get started.\n")
        else:
            for agent in active_agents:
                print(agent.get_status())
                print()

        print(f"Monthly burn rate: ${self.state.get_monthly_burn_rate()}k/quarter")
        print(f"Cash remaining: ${self.state.cash}k\n")

    def hire_agent(self):
        """Allow player to hire an agent"""
        available = [a for a in self.state.available_agents_pool if not any(x.name == a.name for x in self.state.agents)]

        if not available:
            print("\n❌ No available agents to hire!\n")
            return

        if len(self.state.agents) >= 6:
            print("\n❌ You already have the maximum 6 agents!\n")
            return

        print(f"\n{'='*60}")
        print("AVAILABLE AGENTS FOR HIRE")
        print(f"{'='*60}\n")

        for i, agent in enumerate(available, 1):
            print(f"[{i}] {agent.name} - {agent.role.value}")
            print(f"    Skill: {agent.skill_level:.1f} | Specialization: {agent.specialization}")
            print()

        try:
            choice = int(input("Select agent (or 0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(available):
                agent = available[choice - 1]
                self.state.agents.append(agent)
                self.state.available_agents_pool.remove(agent)
                print(f"\n✅ Hired {agent.name}!\n")
            else:
                print("\n❌ Invalid choice.\n")
        except ValueError:
            print("\n❌ Invalid input.\n")

    def fire_agent(self):
        """Allow player to fire an agent"""
        active_agents = [a for a in self.state.agents if not a.is_fired]

        if not active_agents:
            print("\n❌ You have no agents to fire!\n")
            return

        print(f"\n{'='*60}")
        print("FIRE AN AGENT")
        print(f"{'='*60}\n")

        for i, agent in enumerate(active_agents, 1):
            print(f"[{i}] {agent.name} - {agent.role.value}")

        try:
            choice = int(input("Select agent to fire (or 0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(active_agents):
                agent = active_agents[choice - 1]
                confirm = input(f"Are you sure you want to fire {agent.name}? (yes/no): ")
                if confirm.lower() == "yes":
                    agent.is_fired = True
                    self.state.fired_agents.append(agent)
                    self.state.reputation -= 0.2
                    print(f"\n❌ {agent.name} has been fired.")
                    print(f"⚠️  Your reputation dropped by 0.2\n")
        except ValueError:
            print("\n❌ Invalid input.\n")

    def save_game(self):
        """Save current game state"""
        if not self.state:
            print("\n❌ No game in progress.\n")
            return

        filename = self.save_path / f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # Convert to serializable format
        save_data = {
            "player_name": self.state.player_name,
            "quarter": self.state.quarter,
            "cash": self.state.cash,
            "reputation": self.state.reputation,
            "agents": [self._agent_to_dict(a) for a in self.state.agents],
            "projects": [self._project_to_dict(p) for p in self.state.projects],
        }

        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

        print(f"\n✅ Game saved to {filename.name}\n")

    def _agent_to_dict(self, agent: Agent) -> dict:
        return {
            "name": agent.name,
            "role": agent.role.name,
            "skill_level": agent.skill_level,
            "experience": agent.experience,
            "morale": agent.morale,
            "projects_completed": agent.projects_completed,
            "is_fired": agent.is_fired,
        }

    def _project_to_dict(self, project: Project) -> dict:
        return {
            "name": project.name,
            "type": project.project_type.name,
            "complexity": project.complexity,
            "revenue_potential": project.revenue_potential,
            "deadline_quarters": project.deadline_quarters,
            "progress": project.progress,
            "is_completed": project.is_completed,
            "revenue_earned": project.revenue_earned,
        }

    def create_project_menu(self):
        """Create a new project"""
        from game_systems import ProjectManager

        print(f"\n{'='*60}\nNEW PROJECT CREATION\n{'='*60}\n")

        projects = ProjectManager.PROJECT_TEMPLATES
        for i, p in enumerate(projects, 1):
            print(f"[{i}] {p['name']} ({p['type']})")
            print(f"    Revenue: ${p['revenue']}k | Complexity: {p['complexity']:.0%} | Deadline: {p['deadline']} quarters\n")

        try:
            choice = int(input("Select project (or 0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(projects):
                template = projects[choice - 1]
                project = Project(
                    name=template["name"],
                    project_type=ProjectType[template["type"]],
                    complexity=template["complexity"],
                    revenue_potential=template["revenue"],
                    deadline_quarters=template["deadline"],
                )
                self.state.projects.append(project)
                print(f"\n✅ Project '{project.name}' created!\n")
            else:
                print("\n❌ Invalid choice.\n")
        except ValueError:
            print("\n❌ Invalid input.\n")

    def assign_agents_menu(self):
        """Assign agents to projects"""
        active_agents = [a for a in self.state.agents if not a.is_fired]
        unassigned_projects = [p for p in self.state.projects if not p.is_completed and not p.assigned_agents]

        if not active_agents:
            print("\n❌ No agents to assign!\n")
            return

        if not unassigned_projects:
            print("\n❌ No unassigned projects!\n")
            return

        print(f"\n{'='*60}\nASSIGN AGENTS TO PROJECT\n{'='*60}\n")

        for i, p in enumerate(unassigned_projects, 1):
            print(f"[{i}] {p.name} - {p.project_type.value}")
            print(f"    Complexity: {p.complexity:.0%} | Revenue: ${p.revenue_potential}k\n")

        try:
            choice = int(input("Select project (or 0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(unassigned_projects):
                project = unassigned_projects[choice - 1]
                self._select_agents_for_project(project, active_agents)
            else:
                print("\n❌ Invalid choice.\n")
        except ValueError:
            print("\n❌ Invalid input.\n")

    def _select_agents_for_project(self, project, agents):
        """Multi-select agents for a project"""
        print(f"\nAssigning team to '{project.name}':")
        print("Select agents (enter comma-separated numbers, e.g., 1,2,3):\n")

        for i, a in enumerate(agents, 1):
            print(f"[{i}] {a.name} ({a.role.value}) - Skill: {a.skill_level:.1f}")

        try:
            choices_str = input("\nEnter selections: ").strip()
            if not choices_str:
                return

            choices = [int(x.strip()) for x in choices_str.split(",")]
            selected = [agents[i-1] for i in choices if 1 <= i <= len(agents)]

            if selected:
                project.assigned_agents = selected
                print(f"\n✅ Assigned {len(selected)} agents to '{project.name}'!\n")
            else:
                print("\n❌ No valid selections.\n")
        except (ValueError, IndexError):
            print("\n❌ Invalid input.\n")

    def end_quarter(self):
        """Process end of quarter"""
        from game_systems import QuarterlyProcessor, AIGuidance

        print("\n" + "="*60)
        print("PROCESSING QUARTER...")
        print("="*60)

        revenue, summary = QuarterlyProcessor.process_quarter(self.state)
        print(summary)

        if self.state.game_over or self.state.game_won:
            return

        # Show AI guidance
        print("\n" + "="*60)
        print("GEMINI'S QUARTERLY REPORT")
        print("="*60)
        print(AIGuidance.quarterly_review(self.state))
        print("\nRECOMMENDED NEXT STEPS:")
        print(AIGuidance.get_next_steps(self.state))
        print()

    def run(self):
        """Main game loop"""
        print("\n" + "="*60)
        player_name = input("Enter your name: ").strip() or "Manager"
        self.start_new_game(player_name)

        while not self.state.game_over and not self.state.game_won:
            self.display_main_menu()
            try:
                choice = input("> ").strip()

                if choice == "1":
                    self.view_team_status()
                elif choice == "2":
                    self.hire_agent()
                elif choice == "3":
                    self.fire_agent()
                elif choice == "4":
                    self.create_project_menu()
                elif choice == "5":
                    self.assign_agents_menu()
                elif choice == "6":
                    self.end_quarter()
                elif choice == "7":
                    self.gemini_advice()
                elif choice == "8":
                    self.save_game()
                elif choice == "9":
                    print("\n[Feature coming soon: Load game]\n")
                elif choice == "0":
                    confirm = input("Quit game? (yes/no): ")
                    if confirm.lower() == "yes":
                        print("\n👋 Thanks for playing!\n")
                        break
                else:
                    print("\n❌ Invalid choice.\n")
            except KeyboardInterrupt:
                print("\n\n👋 Game interrupted.\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    def gemini_advice(self):
        """Gemini provides guidance"""
        advice = [
            "Build a strong team - hire complementary skills!",
            "Balance profit with team morale. Overworked agents become less productive.",
            "Diversify your projects - don't put all eggs in one basket.",
            "Reputation matters. Bad decisions hurt your ability to hire top talent.",
            "Some projects are worth more than others. Pick your battles wisely.",
            "Keep your cash reserves healthy. Bankruptcy is permanent.",
            "Team synergy matters - compatible agents work better together.",
            "Sometimes firing a dead weight agent is necessary for survival.",
        ]

        import random
        tip = random.choice(advice)

        print(f"""
╔════════════════════════════════════════════════════════════════╗
║ 💬 GEMINI'S TIP                                                ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║ {tip:<60}║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
