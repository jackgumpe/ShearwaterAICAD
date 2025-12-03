#!/usr/bin/env python3
"""
Branch Proxy for the Synaptic Mesh
This script acts as a local hub for agents within a specific domain or "branch".
It uses a ROUTER socket to talk to its connected agents and a DEALER socket
to connect to the Root Router for inter-branch communication.
"""

import zmq
import collections
import json
import time
import logging
import argparse
from pathlib import Path

# --- Logging Setup ---
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


class BranchProxy:
    """
    A class representing a Branch Proxy in the Synaptic Mesh.
    """
    def __init__(self, branch_name: str, branch_port: int, root_host: str = "127.0.0.1", root_port: int = 5550):
        self.branch_name = branch_name
        self.branch_port = branch_port
        self.root_router_address = f"tcp://{root_host}:{root_port}"
        
        self.logger = logging.getLogger(f"BranchProxy-{self.branch_name}")
        handler = logging.FileHandler(LOG_DIR / f"branch_proxy_{self.branch_name}.log")
        handler.setFormatter(logging.Formatter('[%(asctime)s] {%(levelname)s} - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

        self.context = zmq.Context()
        # ROUTER socket for agents to connect to
        self.agent_router = self.context.socket(zmq.ROUTER)
        # DEALER socket to connect to the Root Router
        self.root_dealer = self.context.socket(zmq.DEALER)
        self.root_dealer.identity = f"branch_{self.branch_name}".encode('utf-8')
        
        self.poller = zmq.Poller()
        self.connected_agents = {} # For tracking agents

    def run(self):
        """Starts the Branch Proxy's main loop."""
        self.agent_router.bind(f"tcp://*:{self.branch_port}")
        self.root_dealer.connect(self.root_router_address)
        
        self.logger.info(f"[*] Branch Proxy '{self.branch_name}' started on port {self.branch_port}")
        self.logger.info(f"[*] Connected to Root Router at {self.root_router_address}")

        self.poller.register(self.agent_router, zmq.POLLIN)
        self.poller.register(self.root_dealer, zmq.POLLIN)
        
        try:
            while True:
                events = dict(self.poller.poll(1000))
                self._handle_agent_messages(events)
                self._handle_root_messages(events)

        except KeyboardInterrupt:
            self.logger.info(f"Branch Proxy '{self.branch_name}' shutting down...")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        finally:
            self.stop()

    def _handle_agent_messages(self, events):
        if self.agent_router in events:
            # ROUTER socket receives [sender_identity, payload]
            sender_identity, payload_str = self.agent_router.recv_multipart()
            
            self.logger.info(f"Received message from agent '{sender_identity.decode()}'")
            try:
                msg_data = json.loads(payload_str)
                message_type = msg_data.get("type")

                if message_type == "handshake":
                    self.logger.info(f"Received handshake from '{sender_identity.decode()}'. Acknowledged.")
                    # Handshake messages are not routed further by the proxy, they just register identity.
                    return 

                destination = msg_data.get("to")

                if not destination:
                    self.logger.warning("Message received with no destination, cannot route.")
                    return

                # Forward to the root router as [destination, original_sender, payload]
                self.root_dealer.send_multipart([destination.encode(), sender_identity, payload_str])
                self.logger.info(f"Forwarded message from '{sender_identity.decode()}' to Root Router for '{destination}'")

            except json.JSONDecodeError:
                self.logger.error("Received non-JSON message from agent, cannot route.")

    def _handle_root_messages(self, events):
        if self.root_dealer in events:
            # Format: [destination_identity, original_sender_identity, json_payload]
            destination_identity, original_sender_identity, payload_str = self.root_dealer.recv_multipart()
            
            self.logger.info(f"Received message from Root Router for agent '{destination_identity.decode()}'")
            
            # Forward the message to the correct agent connected to this branch
            self.agent_router.send_multipart([destination_identity, original_sender_identity, payload_str])
            self.logger.info(f"Forwarded message to agent '{destination_identity.decode()}'")

    def stop(self):
        """Stops the proxy and cleans up resources."""
        self.agent_router.close()
        self.root_dealer.close()
        if not self.context.closed:
            self.context.term()
        self.logger.info(f"Branch Proxy '{self.branch_name}' stopped.")


def main():
    """Parses arguments and runs the Branch Proxy."""
    parser = argparse.ArgumentParser(description="Run a Synaptic Mesh Branch Proxy.")
    parser.add_argument("--name", type=str, required=True, help="The name of the branch (e.g., 'core', 'photogrammetry').")
    parser.add_argument("--port", type=int, required=True, help="The port for this branch proxy to listen on.")
    parser.add_argument("--root-port", type=int, default=5550, help="The port of the Root Router.")
    parser.add_argument("--root-host", type=str, default="127.0.0.1", help="The host of the Root Router.")
    
    args = parser.parse_args()
    
    proxy = BranchProxy(
        branch_name=args.name,
        branch_port=args.port,
        root_host=args.root_host,
        root_port=args.root_port
    )
    proxy.run()

if __name__ == "__main__":
    main()
