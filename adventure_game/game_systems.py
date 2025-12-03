# -*- coding: utf-8 -*-
"""
Advanced game systems for LLM Team Manager
Handles quarterly processing, project management, and financial calculations
"""

import sys
import io
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum
import random

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class QuarterlyProcessor:
    """Handles end-of-quarter calculations and reviews"""

    @staticmethod
    def process_quarter(game_state) -> Tuple[int, str]:
        """
        Process end of quarter: project progress, revenue, morale changes, reviews
        Returns: (revenue_earned, quarter_summary_text)
        """
        summary = f"\n{'='*60}\nQUARTERLY REVIEW - Q{game_state.quarter}\n{'='*60}\n"

        # Process active projects
        total_revenue = 0
        completed_projects = []

        for project in game_state.projects:
            if project.is_completed:
                continue

            if not project.assigned_agents:
                summary += f"❌ {project.name} - NO TEAM ASSIGNED\n"
                continue

            # Calculate project progress
            team_productivity = sum(a.get_productivity() for a in project.assigned_agents) / len(project.assigned_agents)
            progress_increment = team_productivity * 0.3  # 30% progress per quarter max

            project.progress = min(1.0, project.progress + progress_increment)

            if project.progress >= 1.0:
                # Project completed
                project.is_completed = True
                project.completion_quarter = game_state.quarter

                # Calculate revenue with bonuses/penalties
                base_revenue = project.revenue_potential
                if project.completion_quarter <= project.deadline_quarters:
                    base_revenue = int(base_revenue * 1.2)  # 20% bonus for on-time
                else:
                    base_revenue = int(base_revenue * 0.7)  # 30% penalty for late

                project.revenue_earned = base_revenue
                total_revenue += base_revenue

                # Increase morale for completing agents
                for agent in project.assigned_agents:
                    agent.morale = min(1.0, agent.morale + 0.1)
                    agent.projects_completed += 1

                completed_projects.append(project)
                summary += f"✅ {project.name} COMPLETED! Revenue: ${base_revenue}k\n"
            else:
                # Project in progress
                progress_pct = int(project.progress * 100)
                summary += f"▓ {project.name} - {progress_pct}% complete\n"

        # Process agent morale decay (overwork)
        active_agents = [a for a in game_state.agents if not a.is_fired]
        for agent in active_agents:
            # Morale decreases based on workload
            if agent in [a for p in game_state.projects if not p.is_completed for a in p.assigned_agents]:
                agent.morale = max(0.1, agent.morale - 0.05)  # Working hard
            else:
                agent.morale = min(1.0, agent.morale + 0.1)  # Resting

        # Calculate costs
        operational_costs = game_state.get_monthly_burn_rate()
        net_profit = total_revenue - operational_costs

        # Update financial state
        game_state.cash += net_profit
        game_state.quarter += 1

        summary += f"\n{'─'*60}\n"
        summary += f"Operations Cost: -${operational_costs}k\n"
        summary += f"Revenue Earned: +${total_revenue}k\n"
        summary += f"Net Profit: ${net_profit}k\n"
        summary += f"Cash Position: ${game_state.cash}k\n"
        summary += f"{'─'*60}\n"

        # Check for end game conditions
        if game_state.cash < 0:
            summary += "\n💥 BANKRUPTCY! Your company has failed. GAME OVER.\n"
            game_state.game_over = True

        if game_state.quarter > 8:
            summary += "\n🏆 You've survived 8 quarters! GAME WON!\n"
            game_state.game_won = True

        return total_revenue, summary


class ProjectManager:
    """Handles project creation and assignment"""

    PROJECT_TEMPLATES = [
        {
            "name": "Mobile Chat App",
            "type": "SAAS",
            "complexity": 0.6,
            "revenue": 500,
            "deadline": 3,
        },
        {
            "name": "Game Engine Framework",
            "type": "GAME",
            "complexity": 0.8,
            "revenue": 800,
            "deadline": 4,
        },
        {
            "name": "Data Analytics Platform",
            "type": "SAAS",
            "complexity": 0.7,
            "revenue": 600,
            "deadline": 3,
        },
        {
            "name": "ML Training Pipeline",
            "type": "AI_TOOL",
            "complexity": 0.9,
            "revenue": 1000,
            "deadline": 5,
        },
        {
            "name": "Cloud Infrastructure",
            "type": "INFRASTRUCTURE",
            "complexity": 0.7,
            "revenue": 700,
            "deadline": 4,
        },
        {
            "name": "Video Processing API",
            "type": "SAAS",
            "complexity": 0.75,
            "revenue": 550,
            "deadline": 3,
        },
        {
            "name": "AI Chatbot Framework",
            "type": "AI_TOOL",
            "complexity": 0.85,
            "revenue": 900,
            "deadline": 4,
        },
        {
            "name": "Search Engine Optimization",
            "type": "RESEARCH",
            "complexity": 0.6,
            "revenue": 400,
            "deadline": 2,
        },
    ]

    @staticmethod
    def create_project(game_state, project_type: str = "random") -> object:
        """Create a new project from templates"""
        from main import Project, ProjectType

        template = random.choice(ProjectManager.PROJECT_TEMPLATES)
        project = Project(
            name=template["name"],
            project_type=ProjectType[template["type"]],
            complexity=template["complexity"],
            revenue_potential=template["revenue"],
            deadline_quarters=template["deadline"],
        )
        game_state.projects.append(project)
        return project

    @staticmethod
    def suggest_project(game_state) -> str:
        """Get AI suggestion on which project to pursue"""
        suggestions = [
            "High-complexity projects take longer but pay better. Invest in experienced teams.",
            "Quick projects with short deadlines can generate cash quickly for more hiring.",
            "Balance your portfolio - don't put all resources into one massive project.",
            "Research projects pay less but build team reputation and skills.",
            "Always have at least one project running per quarter for steady revenue.",
        ]
        return random.choice(suggestions)


class AIGuidance:
    """Represents Gemini AI supervisor guidance"""

    @staticmethod
    def quarterly_review(game_state) -> str:
        """Get AI feedback on quarterly performance"""
        messages = []

        # Financial feedback
        if game_state.cash > 2000:
            messages.append("💰 Excellent cash position. Consider expanding your team!")
        elif game_state.cash < 300:
            messages.append("⚠️  CRITICAL: Low cash. You need revenue NOW!")
        elif game_state.cash < 700:
            messages.append("⚠️  WARNING: Tight cash reserves. Complete a project soon.")

        # Team feedback
        active = [a for a in game_state.agents if not a.is_fired]
        if len(active) < 3:
            messages.append("📉 Small team. Consider hiring to handle more projects.")
        elif len(active) == 6:
            messages.append("📈 Full team assembled. Maximize their potential!")

        avg_morale = sum(a.morale for a in active) / len(active) if active else 0.5
        if avg_morale < 0.4:
            messages.append("😟 Team morale is low. They may leave or perform poorly.")
        elif avg_morale > 0.8:
            messages.append("😊 Team morale is high. Keep momentum!")

        # Project feedback
        completed = len([p for p in game_state.projects if p.is_completed])
        if completed == 0:
            messages.append("🚀 You haven't completed any projects yet. Time to deliver!")
        else:
            messages.append(f"✅ {completed} projects delivered. Building track record!")

        # Reputation
        if game_state.reputation > 0.8:
            messages.append("⭐ Your reputation is stellar. Hire top talent!")
        elif game_state.reputation < 0.3:
            messages.append("💔 Low reputation. Quality hires will be harder to find.")

        return "\n".join(messages)

    @staticmethod
    def get_next_steps(game_state) -> str:
        """Get recommendation on immediate next actions"""
        next_steps = []

        active = [a for a in game_state.agents if not a.is_fired]
        if len(active) < 3:
            next_steps.append("[1] Hire more agents to handle projects")

        unassigned = [p for p in game_state.projects if not p.assigned_agents]
        if unassigned:
            next_steps.append("[2] Assign agents to waiting projects")

        if not any(not p.is_completed for p in game_state.projects):
            next_steps.append("[3] Create new projects to generate revenue")

        if game_state.cash < 500:
            next_steps.append("[4] URGENT: Get projects completed for revenue!")

        return "\n".join(next_steps) if next_steps else "All systems operational. Execute your strategy!"
