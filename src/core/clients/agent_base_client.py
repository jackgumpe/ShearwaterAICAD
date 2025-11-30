#!/usr/bin/env python3
"""
Agent Base Client for Synaptic Mesh Architecture

All agents (Claude, Gemini, etc.) inherit from this class to gain:
- ZeroMQ DEALER socket connection to branch proxy
- Automatic reconnection handling
- Message sending/receiving interface
- Routing utilities
"""

import zmq
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import socket


class AgentBaseClient:
    """
    Base class for all Synaptic Core agents, using a PUB-SUB pattern.
    """

    def __init__(self, agent_name: str,
                 broker_host: str = "localhost", 
                 pub_port: int = 5555,   # Port to publish messages to (XSUB)
                 sub_port: int = 5556):  # Port to subscribe to messages from (XPUB)
        self.agent_name = agent_name
        self.broker_host = broker_host
        self.pub_port = pub_port
        self.sub_port = sub_port
        
        self.is_connected = False
        self.context = None
        self.pub_socket = None # PUB socket for sending messages
        self.sub_socket = None # SUB socket for receiving messages
        
        self.sent_messages = []
        self.received_messages = []
        
        LOG_DIR = Path("logs")
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"Agent-{agent_name}")
        handler = logging.FileHandler(LOG_DIR / f"agent_{agent_name}.log")
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

        # Persistence layer socket for recording messages
        self.persistence_socket = None
        self.persistence_port = 5557  # Dedicated persistence layer port

    def _publish_to_persistence(self, event_type: str, message: Dict[str, Any]) -> None:
        """
        Automatically publish messages to the persistence layer for recording.
        This is Option A: Message hook integration - publish after processing.
        """
        try:
            if not self.context:
                return  # Not yet connected

            # Lazy initialization of persistence socket
            if self.persistence_socket is None:
                self.persistence_socket = self.context.socket(zmq.PUB)
                self.persistence_socket.connect(f"tcp://{self.broker_host}:{self.persistence_port}")
                time.sleep(0.1)  # Brief connection stabilization

            # Wrap message with event metadata
            persistence_event = {
                'event_type': event_type,  # 'sent' or 'received'
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat(),
                'message': message
            }

            # Publish to persistence layer with agent name as topic
            topic = f"persistence.{self.agent_name}".encode('utf-8')
            payload = json.dumps(persistence_event).encode('utf-8')
            self.persistence_socket.send_multipart([topic, payload], flags=zmq.NOBLOCK)

        except zmq.error.Again:
            pass  # Non-blocking send failed, persistence daemon may not be running
        except Exception as e:
            # Log but don't fail - persistence is optional
            self.logger.debug(f"Could not publish to persistence layer: {e}")

    def connect(self) -> bool:
        if self.is_connected:
            self.logger.warning("Already connected.")
            return True
        
        self.context = zmq.Context()
        try:
            # --- Publisher Socket ---
            self.pub_socket = self.context.socket(zmq.PUB)
            self.pub_socket.connect(f"tcp://{self.broker_host}:{self.pub_port}")
            self.logger.info(f"Publisher connected to tcp://{self.broker_host}:{self.pub_port}")

            # --- Subscriber Socket ---
            self.sub_socket = self.context.socket(zmq.SUB)
            self.sub_socket.connect(f"tcp://{self.broker_host}:{self.sub_port}")
            
            # Subscribe to our own agent name as a topic
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, self.agent_name)
            self.logger.info(f"Subscriber connected and subscribed to topic '{self.agent_name}'")
            
            self.is_connected = True
            # Allow robust time for connections to establish and subscriptions to be processed by the broker
            time.sleep(1.5)
            self.logger.info(f"[CONNECTED] Agent '{self.agent_name}' is online.")
            return True
        except Exception as e:
            self.logger.error(f"[FAILED] Could not connect: {e}", exc_info=True)
            return False

    def disconnect(self):
        if self.pub_socket:
            self.pub_socket.close()
        if self.sub_socket:
            self.sub_socket.close()
        if self.persistence_socket:
            self.persistence_socket.close()
        if self.context:
            self.context.term()

        self.pub_socket = self.sub_socket = self.persistence_socket = self.context = None
        self.is_connected = False
        self.logger.info(f"[DISCONNECTED] Agent '{self.agent_name}' disconnected")

    def send_message(self, to_agent: str, message_type: str, content: Dict[str, Any],
                    priority: str = "NORMAL") -> bool:
        if not self.is_connected:
            self.logger.error(f"[ERROR] Not connected. Cannot send message to {to_agent}")
            return False
        try:
            msg_payload = {
                'message_id': f"{self.agent_name}_{int(time.time()*1000)}",
                'timestamp': datetime.now().isoformat(),
                'from': self.agent_name,
                'to': to_agent,
                'type': message_type,
                'priority': priority,
                'content': content
            }
            
            # Publish as a multipart message: [topic, payload]
            topic = to_agent.encode('utf-8')
            payload_str = json.dumps(msg_payload).encode('utf-8')
            
            self.pub_socket.send_multipart([topic, payload_str])

            self.sent_messages.append(msg_payload)
            self.logger.info(f"[SENT] Message to '{to_agent}' on topic '{to_agent}' (type: {message_type})")

            # Automatically publish to persistence layer for recording
            self._publish_to_persistence('sent', msg_payload)

            return True
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to send message: {e}", exc_info=True)
            self.is_connected = False
            return False

    def receive_message(self, timeout_ms: int = 1000) -> Optional[Dict[str, Any]]:
        if not self.is_connected:
            return None
        try:
            # Set a timeout on the receive operation
            if self.sub_socket.poll(timeout_ms):
                # Receive a multipart message: [topic, payload]
                topic_bytes, payload_bytes = self.sub_socket.recv_multipart()
                
                msg = json.loads(payload_bytes.decode('utf-8'))

                self.received_messages.append(msg)
                self.logger.info(f"[RECEIVED] Message from '{msg.get('from')}' via topic '{topic_bytes.decode()}'")

                # Automatically publish to persistence layer for recording
                self._publish_to_persistence('received', msg)

                self.process_incoming_message(msg)
                return msg
            else:
                # Timeout occurred, no message received
                return None
        except zmq.error.Again:
            return None # Expected when no message
        except Exception as e:
            self.logger.error(f"An error occurred in receive_message: {e}", exc_info=True)
            self.is_connected = False
            return None

    def process_incoming_message(self, message: Dict[str, Any]):
        """Hook method for processing incoming messages. Subclasses override this."""
        self.logger.debug(f"Message received by {self.agent_name}: {message.get('message_id')}")

    def broadcast_message(self, message_type: str, content: Dict[str, Any],
                         priority: str = "NORMAL") -> int:
        self.logger.info(f"[BROADCAST] Broadcasting {message_type} message (Phase 2)")
        return 0

    def get_message_history(self) -> Dict[str, list]:
        return {'sent': self.sent_messages, 'received': self.received_messages}

    def save_message_history(self):
        try:
            LOG_DIR = Path("logs")
            filename = LOG_DIR / f"agent_{self.agent_name}_messages.json"
            history = {
                'agent': self.agent_name,
                'branch': self.branch_name,
                'sent_count': len(self.sent_messages),
                'received_count': len(self.received_messages),
                'sent': self.sent_messages,
                'received': self.received_messages
            }
            with open(filename, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            self.logger.info(f"Message history saved to {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save message history: {e}", exc_info=True)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_message_history()
        self.disconnect()
        return False


if __name__ == "__main__":
    print("Agent Base Client - Ready for inheritance")
