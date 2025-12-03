#!/usr/bin/env python3
"""
ZMQ Message Sender
Reads a JSON file and publishes its content to the ZeroMQ broker.
"""

import zmq
import json
import sys
import time

# --- Configuration ---
BROKER_PUB_PORT = 5555  # The port for publishers on the broker
BROKER_ADDRESS = "127.0.0.1"
DEFAULT_TOPIC = "gemini_response"

def main():
    """
    Main function to send a message.
    """
    if len(sys.argv) < 2:
        print("Usage: python send_message.py <path_to_json_file> [topic]")
        sys.exit(1)

    file_path = sys.argv[1]
    topic = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TOPIC

    try:
        with open(file_path, 'r') as f:
            message_content = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in file: {file_path}")
        sys.exit(1)

    context = zmq.Context()
    
    # --- Socket to send messages ---
    publisher = context.socket(zmq.PUB)
    publisher.connect(f"tcp://{BROKER_ADDRESS}:{BROKER_PUB_PORT}")

    # Give the connection a moment to establish
    time.sleep(1)

    try:
        # --- Prepare the message ---
        # The message format is [topic, json_payload]
        payload = json.dumps(message_content)
        
        # --- Send the message ---
        publisher.send_multipart([topic.encode(), payload.encode()])
        
        print(f"[SENT] Message from {file_path} on topic '{topic}'")
        print(f"[CONTENT] {payload}")

    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
    finally:
        publisher.close()
        context.term()

if __name__ == "__main__":
    main()
