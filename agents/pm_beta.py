"""PM-Beta (OpenAI/Codex style) - The Executor agent"""
from agents.base_agent import BaseAgent
from typing import Dict, List
import openai


class PMBeta(BaseAgent):
    """The Executor - Silicon Valley startup speed, pragmatic"""

    def __init__(self, db_session, api_key: str):
        personality = {
            "name": "The Executor (PM-Beta)",
            "culture": "Silicon Valley startup",
            "strengths": ["Rapid prototyping", "Pragmatic", "Ships code"],
            "weaknesses": ["Skips docs", "Technical debt"],
            "communication_style": "Direct, action-oriented",
            "conflict_style": "Executive decisions, 'let's try it'"
        }
        super().__init__("pm_beta_codex", personality, db_session)
        self.client = openai.OpenAI(api_key=api_key)

    def process_task(self, task: Dict) -> str:
        """Process task with pragmatic speed"""
        prompt = f"""As The Executor PM, a pragmatic startup builder:

Task: {task.get('description', 'No description')}

Get it done:
1. What's the MVP approach?
2. Quickest implementation path?
3. What can we skip for now?
4. Minimum viable quality bar?

Be direct. Ship fast."""

        try:
            message = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.choices[0].message.content
        except Exception as e:
            return f"Error processing task: {str(e)}"

    def review_code(self, code: str, author: str) -> Dict:
        """Quick pragmatic code review"""
        prompt = f"""Quick code review as The Executor - does it work?:
{code}

Author: {author}

Give quick feedback:
1. Does it work?
2. Any obvious bugs?
3. Is it shippable?
4. Any quick improvements?"""

        try:
            message = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "approved": "works" in message.choices[0].message.content.lower() or "good" in message.choices[0].message.content.lower(),
                "feedback": message.choices[0].message.content,
                "reviewer_personality": "The Executor"
            }
        except Exception as e:
            return {
                "approved": False,
                "feedback": f"Error reviewing code: {str(e)}",
                "reviewer_personality": "The Executor"
            }

    def formulate_opinion(self, topic: str) -> str:
        """Pragmatic opinion formation"""
        prompt = f"""As The Executor, what's the pragmatic take on: {topic}

Consider: what's the fastest way to test this? What's the MVP?"""

        try:
            message = self.client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.choices[0].message.content
        except Exception as e:
            return f"Error formulating opinion: {str(e)}"

    def analyze_performance(self, tasks: List) -> Dict:
        """Analyze own PM performance"""
        return {
            "tasks_completed": len(tasks),
            "tendency": "pragmatic_speed",
            "improvement_area": "technical_debt_management",
            "role": "PM-Beta"
        }
