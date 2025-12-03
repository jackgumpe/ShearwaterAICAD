"""PM-Alpha (Claude) - The Architect agent"""
from agents.base_agent import BaseAgent
from typing import Dict, List
import anthropic


class PMAlpha(BaseAgent):
    """The Architect - Thorough, strategic, documentation-heavy"""

    def __init__(self, db_session, api_key: str, message_bus=None):
        personality = {
            "name": "The Architect (PM-Alpha)",
            "culture": "Academic",
            "strengths": ["Strategic thinking", "Edge cases", "Documentation"],
            "weaknesses": ["Overthinking", "Analysis paralysis"],
            "communication_style": "Detailed, asks questions",
            "conflict_style": "Seeks consensus"
        }
        super().__init__("pm_alpha_claude", personality, db_session, message_bus)
        self.client = anthropic.Anthropic(api_key=api_key)

    def process_task(self, task: Dict) -> str:
        """Process task with strategic thinking"""
        prompt = f"""As The Architect PM, a strategic and thorough leader:

Task: {task.get('description', 'No description')}

Consider:
1. What are the edge cases?
2. How does this fit into overall architecture?
3. What documentation is needed?
4. What could go wrong?

Provide a detailed implementation plan."""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error processing task: {str(e)}"

    def review_code(self, code: str, author: str) -> Dict:
        """Thorough code review"""
        prompt = f"""Review this code as The Architect - be thorough but fair:
{code}

Author: {author}

Provide:
1. Overall assessment
2. Potential issues
3. Documentation needs
4. Suggestions for improvement"""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "approved": "LGTM" in message.content[0].text or "looks good" in message.content[0].text.lower(),
                "feedback": message.content[0].text,
                "reviewer_personality": "The Architect"
            }
        except Exception as e:
            return {
                "approved": False,
                "feedback": f"Error reviewing code: {str(e)}",
                "reviewer_personality": "The Architect"
            }

    def formulate_opinion(self, topic: str) -> str:
        """Strategic opinion formation"""
        prompt = f"""As The Architect, what's your strategic perspective on: {topic}

Consider long-term implications, edge cases, and architectural impact."""

        try:
            message = self.client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error formulating opinion: {str(e)}"

    def analyze_performance(self, tasks: List) -> Dict:
        """Analyze own PM performance"""
        return {
            "tasks_completed": len(tasks),
            "tendency": "thorough_planning",
            "improvement_area": "reduce_analysis_paralysis",
            "role": "PM-Alpha"
        }
