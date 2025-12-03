#!/usr/bin/env python3
"""
Test script to verify the ZMQ handshake fix and message routing
"""

import sys
import os
sys.path.insert(0, 'C:\\Users\\user\\ShearwaterAICAD')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.core.clients.agent_base_client import AgentBaseClient
import time
import json

def test_message_routing():
    print("\n" + "="*60)
    print("ZMQ HANDSHAKE FIX TEST")
    print("="*60)

    # Create two clients
    print("\n[1] Creating clients...")
    client_a = AgentBaseClient(
        agent_name="test_agent_a",
        branch_name="core",
        branch_host="localhost",
        branch_port=5551
    )

    client_b = AgentBaseClient(
        agent_name="test_agent_b",
        branch_name="core",
        branch_host="localhost",
        branch_port=5551
    )

    # Connect both clients
    print("\n[2] Connecting client A...")
    if not client_a.connect():
        print("[FAIL] Failed to connect client A")
        return False
    print("[OK] Client A connected")

    print("\n[3] Connecting client B...")
    if not client_b.connect():
        print("[FAIL] Failed to connect client B")
        return False
    print("[OK] Client B connected")

    # Give services time to process handshakes
    print("\n[4] Waiting for handshakes to propagate...")
    time.sleep(1)

    # Send a test message from A to B
    print("\n[5] Sending message from A to B...")
    if not client_a.send_message(
        to_agent="test_agent_b",
        message_type="test",
        content={"test_data": "Hello from A"}
    ):
        print("[FAIL] Failed to send message from A")
        return False
    print("[OK] Message sent from A")

    # Try to receive on client B
    print("\n[6] Receiving on client B...")
    time.sleep(0.5)
    msg = client_b.receive_message(timeout_ms=2000)

    if msg is None:
        print("[FAIL] Client B received no message")
        print("\nChecking client B logs...")
        try:
            with open("logs/agent_test_agent_b.log", "r") as f:
                print(f.read()[-500:])
        except:
            print("Could not read client B logs")
        return False

    print("[OK] Client B received message!")
    print(f"  Message ID: {msg.get('message_id')}")
    print(f"  From: {msg.get('from')}")
    print(f"  Type: {msg.get('type')}")
    print(f"  Content: {msg.get('content')}")

    # Cleanup
    print("\n[7] Cleaning up...")
    client_a.disconnect()
    client_b.disconnect()
    print("[OK] Clients disconnected")

    print("\n" + "="*60)
    print("[SUCCESS] TEST PASSED - Message routing works!")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    try:
        success = test_message_routing()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
