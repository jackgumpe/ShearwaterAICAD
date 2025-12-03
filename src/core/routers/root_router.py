#!/usr/bin/env python3
"""
Root Router for the Synaptic Mesh
This is the central hub for inter-branch communication.
It uses a ROUTER socket to listen for messages from branch proxies and
forwards them to the correct destination branch proxy.
"""

import zmq
import collections
import json
import time
import logging
from pathlib import Path

# --- Configuration ---
ROOT_ROUTER_PORT = 5550
MAX_MESSAGE_HISTORY = 10000

# --- Logging Setup ---
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] {%(levelname)s} - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_DIR / "root_router.log"),
                        logging.StreamHandler()
                    ])

# --- In-memory message log ---
message_log = collections.deque(maxlen=MAX_MESSAGE_HISTORY)

# --- Agent to Branch Mapping ---

# Maps agent names to their branch's DEALER identity (as bytes).
# Dynamic discovery: When a branch proxy sends a message for an agent,
# we learn that agent's location and cache it.

AGENT_BRANCH_MAP = {
    "claude_code": b"branch_core",
    "gemini_cli": b"branch_core",
}



def main():

    """Starts the Root Router."""

    context = zmq.Context()

    

    # ROUTER socket listens for incoming connections from branch proxies

    router_socket = context.socket(zmq.ROUTER)

    router_socket.bind(f"tcp://*:{ROOT_ROUTER_PORT}")



    logging.info(f"[*] Root Router started on port {ROOT_ROUTER_PORT}")

    logging.info(f"[*] Storing last {MAX_MESSAGE_HISTORY} messages in memory.")

    

    try:

        while True:

            # The router receives [proxy_identity, destination_agent, original_sender, payload].

            proxy_identity, destination_agent, original_sender, payload_str = router_socket.recv_multipart()



            logging.info(f"Received message from proxy '{proxy_identity.decode()}' for agent '{destination_agent.decode()}'")



            # Log the message

            try:

                message_log.append(json.loads(payload_str))

            except json.JSONDecodeError:

                logging.error(f"Failed to decode JSON payload from '{proxy_identity.decode()}'")

                continue



            # Look up the destination branch from our map

            dest_agent_str = destination_agent.decode()

            # Try to get from map - returns the branch's DEALER identity as stored
            dest_branch_identity_bytes = AGENT_BRANCH_MAP.get(dest_agent_str)



            if not dest_branch_identity_bytes:

                # Dynamic discovery: For same-branch routing, assume agent is on the same branch as sender.
                # Use proxy_identity directly since the sender knows how to reach this branch.
                dest_branch_identity_bytes = proxy_identity
                logging.info(f"Learning: agent '{dest_agent_str}' is on same branch as sender ('{proxy_identity.decode()}')")
                AGENT_BRANCH_MAP[dest_agent_str] = proxy_identity



            # Forward the message to the correct branch proxy.

            # The router uses the first frame as the address of the recipient proxy.

            # Use the branch's actual DEALER identity bytes for routing.

            router_socket.send_multipart([dest_branch_identity_bytes, destination_agent, original_sender, payload_str])



            logging.info(f"Relayed message for '{dest_agent_str}' to branch '{dest_branch_identity_bytes.decode()}'")



    except KeyboardInterrupt:

        logging.info("Root Router shutting down...")

    except Exception as e:

        logging.error(f"An unexpected error occurred in the Root Router: {e}")

    finally:

        router_socket.close()

        context.term()

        logging.info("Root Router stopped.")





if __name__ == "__main__":

    main()
