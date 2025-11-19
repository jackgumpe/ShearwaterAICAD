"""Base agent class with messaging and reflection capabilities"""
from abc import ABC, abstractmethod
from core.message_bus import MessageBus
from core.database import Conversation, Decision, Reflection
from typing import Dict, List
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BaseAgent(ABC):
    def __init__(self, agent_id: str, personality: Dict, db_session):
        self.agent_id = agent_id
        self.personality = personality
        self.db = db_session
        self.message_bus = MessageBus(agent_id)

        # Subscribe to relevant message types
        self.message_bus.subscribe("task_assignment", self.on_task_assigned)
        self.message_bus.subscribe("code_review_request", self.on_review_request)
        self.message_bus.subscribe("debate_topic", self.on_debate)

    @abstractmethod
    def process_task(self, task: Dict) -> str:
        """Process assigned task"""
        pass

    @abstractmethod
    def review_code(self, code: str, author: str) -> Dict:
        """Review code from another agent"""
        pass

    def on_task_assigned(self, message: Dict):
        """Handle task assignment"""
        task = message["content"]
        result = self.process_task(task)

        # Log to database
        conv = Conversation(
            agent_id=self.agent_id,
            message_type="task_completion",
            content={"task": task, "result": result},
            tier=3
        )
        self.db.add(conv)
        self.db.commit()

        # Broadcast completion
        self.message_bus.publish("task_completed", {
            "task_id": task.get("id", "unknown"),
            "agent": self.agent_id,
            "result": result
        })

    def on_review_request(self, message: Dict):
        """Handle code review request"""
        code = message["content"]["code"]
        author = message["from"]

        review = self.review_code(code, author)

        self.message_bus.publish("code_review_completed", {
            "original_author": author,
            "reviewer": self.agent_id,
            "review": review
        })

    def on_debate(self, message: Dict):
        """Participate in debate"""
        topic = message["content"]["topic"]
        position = self.formulate_opinion(topic)

        self.message_bus.publish("debate_contribution", {
            "topic": topic,
            "agent": self.agent_id,
            "position": position,
            "personality": self.personality["name"]
        })

    @abstractmethod
    def formulate_opinion(self, topic: str) -> str:
        """Form opinion on a topic based on personality"""
        pass

    def reflect(self, reflection_type: str):
        """Self-reflection mechanism"""
        # Retrieve recent activities
        recent_tasks = self.db.query(Conversation).filter_by(
            agent_id=self.agent_id
        ).order_by(Conversation.timestamp.desc()).limit(10).all()

        # Analyze and reflect
        insights = self.analyze_performance(recent_tasks)

        # Store reflection
        reflection = Reflection(
            agent_id=self.agent_id,
            reflection_type=reflection_type,
            content=f"Reflecting on last {len(recent_tasks)} tasks",
            insights=insights
        )
        self.db.add(reflection)
        self.db.commit()

    @abstractmethod
    def analyze_performance(self, tasks: List) -> Dict:
        """Analyze own performance"""
        pass

    def start(self):
        """Start the agent"""
        self.message_bus.start_listening()
