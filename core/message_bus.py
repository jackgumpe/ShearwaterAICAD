"""ZeroMQ-based message bus for inter-agent communication"""
import zmq
import json
import threading
from typing import Dict, Callable
from datetime import datetime


class MessageBus:
    """ZeroMQ-based message bus for inter-agent communication"""

    def __init__(self, agent_id: str, pub_port: int = 5555, sub_port: int = 5556):
        self.agent_id = agent_id
        self.context = zmq.Context()

        # Publisher socket
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{pub_port}")

        # Subscriber socket
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(f"tcp://localhost:{sub_port}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        self.callbacks: Dict[str, Callable] = {}
        self.running = False

    def publish(self, message_type: str, content: dict):
        """Broadcast message to all agents"""
        message = {
            "from": self.agent_id,
            "type": message_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.publisher.send_json(message)

    def subscribe(self, message_type: str, callback: Callable):
        """Register callback for message type"""
        self.callbacks[message_type] = callback

    def start_listening(self):
        """Start listening thread"""
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

    def _listen_loop(self):
        """Internal listening loop"""
        while self.running:
            try:
                message = self.subscriber.recv_json(flags=zmq.NOBLOCK)
                if message["from"] != self.agent_id:
                    msg_type = message["type"]
                    if msg_type in self.callbacks:
                        self.callbacks[msg_type](message)
            except zmq.Again:
                pass

    def stop(self):
        """Stop the message bus"""
        self.running = False
        self.publisher.setsockopt(zmq.LINGER, 0)
        self.subscriber.setsockopt(zmq.LINGER, 0)
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
