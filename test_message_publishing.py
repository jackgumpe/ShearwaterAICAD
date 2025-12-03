#!/usr/bin/env python3
"""Test publishing messages through the broker to verify recording"""

import zmq
import json
import time
from datetime import datetime

context = zmq.Context()

# Create a PUB socket to publish messages
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://localhost:5555")

print("[TEST] Publisher connected to broker at tcp://localhost:5555")

# Wait a moment for the connection to establish
time.sleep(1)

# Publish a test message
test_message = {
    "sender_id": "test_agent",
    "message_id": "test_msg_001",
    "timestamp": datetime.utcnow().isoformat(),
    "content": {
        "message": "This is a test message to verify broker recording"
    },
    "metadata": {
        "sender_role": "Test"
    }
}

topic = b"test_topic"
payload = json.dumps(test_message).encode('utf-8')

print(f"[TEST] Publishing message: {test_message}")
pub_socket.send_multipart([topic, payload])
print("[OK] Message published")

# Publish another message
test_message2 = {
    "sender_id": "test_agent",
    "message_id": "test_msg_002",
    "timestamp": datetime.utcnow().isoformat(),
    "content": {
        "message": "This is a second test message"
    },
    "metadata": {
        "sender_role": "Test"
    }
}

payload2 = json.dumps(test_message2).encode('utf-8')
pub_socket.send_multipart([topic, payload2])
print("[OK] Second message published")

time.sleep(1)

pub_socket.close()
context.term()

print("\n[TEST] Publisher disconnected")
print("[TEST] Checking if messages were recorded...")

# Check the log file
import os
from pathlib import Path

log_file = Path("conversation_logs/current_session.jsonl")
if log_file.exists():
    with open(log_file, 'r') as f:
        lines = f.readlines()

    print(f"[INFO] Log file has {len(lines)} total messages")

    # Find our test messages
    test_msgs = [l for l in lines if 'test message' in l.lower()]
    print(f"[INFO] Found {len(test_msgs)} messages containing 'test message'")

    if test_msgs:
        print("[SUCCESS] Test messages were recorded!")
        print(f"\nFirst test message logged:")
        msg = json.loads(test_msgs[0])
        print(f"  Timestamp: {msg.get('Timestamp')}")
        print(f"  Sender: {msg.get('SpeakerName')}")
        print(f"  ACE Tier: {msg.get('Metadata', {}).get('ace_tier')}")
        print(f"  Chain Type: {msg.get('Metadata', {}).get('chain_type')}")
        print(f"  Tags: {msg.get('Metadata', {}).get('shl_tags')}")
    else:
        print("[WARNING] Test messages NOT found in log file")
else:
    print("[ERROR] Log file does not exist")
