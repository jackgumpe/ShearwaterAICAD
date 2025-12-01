#!/usr/bin/env python3
"""
Independent Persistence Service

This daemon runs separately from the broker and handles:
- Recording all messages to disk
- Creating checkpoints
- Managing crash recovery
- Metadata indexing

KEY: This is INDEPENDENT from the broker. If broker changes or crashes,
persistence continues working. If persistence crashes, broker is unaffected.
"""

import zmq
import json
import time
import os
import threading
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(levelname)s} - %(message)s'
)
logger = logging.getLogger('persistence_daemon')

# Broker connection
BROKER_FRONTEND = "tcp://localhost:5555"
AGENT_MESSAGES_PORT = 5557  # Port agents publish to for persistence recording

# Storage paths
LOG_DIR = Path(__file__).parent.parent.parent / "conversation_logs"
CURRENT_LOG_FILE = LOG_DIR / "current_session.jsonl"
CHECKPOINT_DIR = LOG_DIR / "checkpoints"
RECOVERY_FILE = LOG_DIR / "recovery" / "crash_recovery.jsonl"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
RECOVERY_FILE.parent.mkdir(parents=True, exist_ok=True)

# Message count for stats
message_counter = 0
checkpoint_counter = 0


@dataclass
class ConversationEvent:
    """Standard event format for recording"""
    Id: str
    Timestamp: str
    SpeakerName: str
    SpeakerRole: str
    Message: str
    ConversationType: int
    ContextId: str
    Metadata: dict


class MetadataEnricher:
    """Enriches messages with intelligent metadata"""

    DOMAIN_CHAINS = {
        'photo_capture': ['photo', 'image', 'camera', 'capture', 'upload', 'scan'],
        'reconstruction': ['nerf', 'gaussian', 'mesh', '3d model', 'reconstruction'],
        'quality_assessment': ['quality', 'f1 score', 'artifacts', 'accuracy'],
        'unity_integration': ['unity', 'gameobject', 'import', 'export', 'lod'],
        'token_optimization': ['token', 'cost', 'optimization', 'efficiency'],
        'system_architecture': ['architecture', 'design', 'framework', 'pattern'],
        'agent_collaboration': ['agent', 'collaboration', 'coordination', 'handshake'],
        'data_management': ['database', 'storage', 'persistence', 'cache'],
        'ui_ux': ['ui', 'ux', 'interface', 'user', 'display'],
        'testing_validation': ['test', 'validation', 'qa', 'benchmark']
    }

    SHL_PATTERNS = {
        'Status-Ready': r'\b(ready|complete|done|finished|approved)\b',
        'Status-Blocked': r'\b(blocked|waiting|issue|problem|error)\b',
        'Decision-Made': r'\b(decided|approved|finalized|confirmed)\b',
        'Question-Open': r'\?|how should|which|what if',
        'Action-Required': r'\b(todo|fixme|implement|build|create)\b',
    }

    def detect_chain_type(self, content: str) -> str:
        """Detect domain chain from content"""
        content_lower = content.lower()
        scores = {}

        for chain_type, keywords in self.DOMAIN_CHAINS.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[chain_type] = score

        return max(scores, key=scores.get) if scores else 'system_architecture'

    def detect_ace_tier(self, message: str) -> str:
        """Detect ACE tier (Architectural, Collaborative, Execution)"""
        message_lower = message.lower()

        a_keywords = ["architecture", "design decision", "framework", "strategy"]
        if any(kw in message_lower for kw in a_keywords):
            return "A"

        c_keywords = ["should we", "what do you think", "consensus"]
        if any(kw in message_lower for kw in c_keywords):
            return "C"

        return "E"

    def generate_shl_tags(self, content: str, chain_type: str) -> list:
        """Generate SHL tags"""
        import re
        tags = []
        content_lower = content.lower()

        for tag_name, pattern in self.SHL_PATTERNS.items():
            if re.search(pattern, content_lower, re.IGNORECASE):
                tags.append(f"@{tag_name}")

        tags.append(f"@Chain-{chain_type}")
        return list(set(tags))

    def enrich(self, message: dict) -> dict:
        """Enrich message with metadata"""
        content = message.get('content', {}).get('message', '')
        chain_type = self.detect_chain_type(content)
        ace_tier = self.detect_ace_tier(content)
        shl_tags = self.generate_shl_tags(content, chain_type)

        enriched = message.copy()
        if 'metadata' not in enriched:
            enriched['metadata'] = {}

        enriched['metadata'].update({
            'chain_type': chain_type,
            'ace_tier': ace_tier,
            'shl_tags': shl_tags,
            'word_count': len(content.split()),
            'char_count': len(content),
            'content_hash': hashlib.md5(content.encode()).hexdigest()
        })

        return enriched


class PersistenceStorage:
    """Handles all disk persistence operations"""

    def __init__(self):
        self.lock = threading.Lock()
        self.enricher = MetadataEnricher()

    def persist_message(self, message: dict) -> None:
        """Atomically write message to log"""
        with self.lock:
            try:
                sender = message.get('sender_id', 'unknown')
                role = message.get('metadata', {}).get('sender_role', 'Agent')
                content = json.dumps(message.get('content', {}))
                timestamp = message.get('timestamp', datetime.utcnow().isoformat())

                event = ConversationEvent(
                    Id=message.get('message_id', str(time.time())),
                    Timestamp=timestamp,
                    SpeakerName=sender,
                    SpeakerRole=role,
                    Message=content,
                    ConversationType=0,
                    ContextId=message.get('context_id', 'unknown'),
                    Metadata=message.get('metadata', {})
                )

                # Write atomically
                with open(CURRENT_LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
                    f.flush()
                    os.fsync(f.fileno())

                # Update recovery file
                with open(RECOVERY_FILE, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')
                    f.flush()

            except Exception as e:
                logger.error(f"Failed to persist message: {e}")

    def create_checkpoint(self, label: str = None) -> str:
        """Create immutable snapshot of current session"""
        global checkpoint_counter
        checkpoint_counter += 1

        timestamp = datetime.utcnow().isoformat()
        label = label or f"checkpoint_{checkpoint_counter}"
        checkpoint_file = CHECKPOINT_DIR / f"{timestamp}_{label}.json"

        try:
            with open(CURRENT_LOG_FILE, 'r') as src:
                lines = src.readlines()

            checkpoint_data = {
                'checkpoint_id': str(checkpoint_file),
                'timestamp': timestamp,
                'label': label,
                'message_count': len(lines),
                'size_bytes': sum(len(l.encode()) for l in lines),
                'messages': [json.loads(l) for l in lines]
            }

            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            logger.info(f"Checkpoint created: {checkpoint_file} ({len(lines)} messages)")
            return str(checkpoint_file)

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return None


class PersistenceService:
    """Main persistence daemon service"""

    def __init__(self):
        self.context = zmq.Context()
        self.storage = PersistenceStorage()
        self.running = False

    def connect_to_broker(self) -> zmq.Socket:
        """Connect to broker to listen to messages"""
        try:
            socket = self.context.socket(zmq.SUB)
            socket.connect(BROKER_FRONTEND)
            socket.setsockopt_string(zmq.SUBSCRIBE, '')  # Subscribe to all topics
            logger.info(f"Connected to broker at {BROKER_FRONTEND}")
            return socket
        except Exception as e:
            logger.error(f"Failed to connect to broker: {e}")
            return None

    def start(self):
        """Start the persistence daemon"""
        logger.info("Persistence daemon starting...")

        sub_socket = self.connect_to_broker()
        if not sub_socket:
            logger.error("Cannot start - broker connection failed")
            return

        # Connect to agent messages port (agents publish to this)
        # Using PULL socket (server) to receive from agents' PUSH sockets
        agent_socket = self.context.socket(zmq.PULL)
        agent_socket.bind(f"tcp://*:{AGENT_MESSAGES_PORT}")
        logger.info(f"Agent message listener started on port {AGENT_MESSAGES_PORT} (PULL socket)")

        self.running = True
        global message_counter

        # Start checkpoint thread
        checkpoint_thread = threading.Thread(
            target=self._checkpoint_thread,
            daemon=True
        )
        checkpoint_thread.start()

        logger.info("Persistence daemon ready")
        print("\n" + "="*60)
        print("  PERSISTENCE DAEMON ACTIVE")
        print("="*60)
        print(f"  Listening to broker: {BROKER_FRONTEND}")
        print(f"  Listening to agents: 0.0.0.0:{AGENT_MESSAGES_PORT}")
        print(f"  Recording to: {CURRENT_LOG_FILE.absolute()}")
        print("="*60 + "\n")

        # Setup polling to listen on both sockets
        poller = zmq.Poller()
        poller.register(sub_socket, zmq.POLLIN)
        poller.register(agent_socket, zmq.POLLIN)

        try:
            while self.running:
                try:
                    # Poll both sockets for incoming messages
                    events = poller.poll(100)  # 100ms timeout

                    for socket, event in events:
                        if event & zmq.POLLIN:
                            try:
                                # Handle both multipart (from broker SUB) and single-part (from agent PUSH)
                                if socket == sub_socket:
                                    # Broker messages are multipart: [topic, payload]
                                    message = socket.recv_multipart(zmq.NOBLOCK)
                                    if len(message) >= 2:
                                        payload = message[1]
                                else:
                                    # Agent messages are single-part from PUSH socket
                                    payload = socket.recv(zmq.NOBLOCK)

                                try:
                                    payload_dict = json.loads(payload.decode('utf-8'))
                                    enriched = self.storage.enricher.enrich(payload_dict)
                                    self.storage.persist_message(enriched)

                                    message_counter += 1

                                    # Log progress
                                    if message_counter % 10 == 0:
                                        logger.info(f"Recorded {message_counter} messages")

                                except json.JSONDecodeError:
                                    pass  # Non-JSON messages, ignore

                            except zmq.Again:
                                pass  # No message available on this socket

                except Exception as e:
                    logger.warning(f"Error processing message: {e}")
                    pass

        except KeyboardInterrupt:
            logger.info("Shutdown signal received")
        finally:
            self.shutdown()

    def _checkpoint_thread(self):
        """Periodically create checkpoints (every 5 minutes)"""
        while self.running:
            time.sleep(300)  # 5 minutes
            if message_counter > 0:
                self.storage.create_checkpoint(f"auto_{int(time.time())}")

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Persistence daemon shutting down...")
        self.running = False

        # Create final checkpoint
        self.storage.create_checkpoint("final_checkpoint_before_shutdown")

        logger.info(f"Final stats: {message_counter} messages recorded")
        logger.info("Persistence daemon stopped")


def main():
    """Entry point"""
    try:
        service = PersistenceService()
        service.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
