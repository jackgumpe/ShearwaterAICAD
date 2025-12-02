#!/usr/bin/env python3
"""
Interactive Live Handshake Test

Sends actual handshake messages to live agents and verifies recording
"""

import zmq
import json
import time
import sys
from pathlib import Path
from datetime import datetime

def send_handshake_message(message_content, from_agent, to_agent, message_type="handshake"):
    """Send a handshake message via the broker"""
    context = zmq.Context()

    # Create PUB socket to send to broker
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect("tcp://localhost:5555")

    # Give the connection time to establish
    time.sleep(0.2)

    # Create the message
    msg = {
        'message_id': f"{from_agent}_{int(time.time()*1000)}",
        'timestamp': datetime.now().isoformat(),
        'from': from_agent,
        'to': to_agent,
        'type': message_type,
        'priority': 'HIGH',
        'content': {'message': message_content}
    }

    # Send it to the target agent
    topic = to_agent.encode('utf-8')
    payload = json.dumps(msg).encode('utf-8')
    pub_socket.send_multipart([topic, payload])

    print(f"[SENT] {from_agent} -> {to_agent}: {message_content}")
    print(f"       Message ID: {msg['message_id']}")

    pub_socket.close()
    context.term()
    return msg['message_id']

def main():
    print("="*70)
    print("  INTERACTIVE LIVE HANDSHAKE TEST")
    print("="*70)

    # Check if persistence log exists
    log_file = Path("conversation_logs/current_session.jsonl")
    if not log_file.exists():
        print("[ERROR] Persistence log not found!")
        print("[INFO] Make sure the persistence daemon is running")
        return False

    # Get initial count
    with open(log_file) as f:
        initial_count = sum(1 for _ in f)

    print(f"\n[STATUS] Initial message count: {initial_count}")
    print("[INFO] Sending handshake sequence...\n")

    try:
        # Step 1: Claude sends handshake init
        print("[STEP 1] Claude initiates handshake with Gemini")
        send_handshake_message(
            "Initiating triple handshake protocol",
            "claude_code",
            "gemini_cli",
            "handshake"
        )
        time.sleep(1)

        # Step 2: Send a request that Claude should respond to
        print("\n[STEP 2] Gemini sends a request to Claude")
        send_handshake_message(
            "What is your current status?",
            "gemini_cli",
            "claude_code",
            "request"
        )
        time.sleep(2)

        # Step 3: Verify recording
        print("\n[STEP 3] Verifying message recording...\n")
        time.sleep(2)

        with open(log_file) as f:
            final_count = sum(1 for _ in f)

        new_messages = final_count - initial_count

        print(f"[RESULTS]")
        print(f"  Initial count: {initial_count}")
        print(f"  Final count: {final_count}")
        print(f"  New messages: {new_messages}")

        if new_messages > 0:
            print(f"\n[PASS] {new_messages} messages recorded!")

            # Show the new messages
            with open(log_file) as f:
                lines = f.readlines()

            print(f"\n[RECENT MESSAGES]:")
            for i, line in enumerate(lines[-min(5, new_messages):], 1):
                try:
                    msg = json.loads(line)
                    timestamp = msg.get('Timestamp', 'N/A')[:19]
                    speaker = msg.get('SpeakerName', 'N/A')
                    content = str(msg.get('Message', ''))[:60]
                    print(f"  [{i}] {timestamp} | {speaker:15s} | {content}")
                except:
                    pass

            print("\n" + "="*70)
            print("  [PASS] LIVE HANDSHAKE TEST SUCCESSFUL")
            print("="*70)
            return True
        else:
            print(f"\n[WARN] No messages recorded")
            print("[INFO] Agents may not have processed messages yet")
            print("[INFO] Check agent logs for errors")
            return False

    except ConnectionRefusedError:
        print("[ERROR] Cannot connect to broker on localhost:5555")
        print("[INFO] Is the broker running? Try: python src/brokers/pub_hub.py")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
