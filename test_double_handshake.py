#!/usr/bin/env python3
"""
Test double handshake between agents with persistence recording

This simulates claude_code and gemini_cli agents performing a handshake
and verifies that all messages are being recorded to the persistence layer.
"""

import zmq
import json
import time
from datetime import datetime
from pathlib import Path

def create_agent_message(from_agent, to_agent, message_type, content):
    """Create a properly formatted agent message"""
    return {
        'message_id': f"{from_agent}_{int(time.time()*1000)}",
        'timestamp': datetime.now().isoformat(),
        'from': from_agent,
        'to': to_agent,
        'type': message_type,
        'priority': 'NORMAL',
        'content': content
    }

def test_double_handshake():
    print("="*70)
    print("  DOUBLE HANDSHAKE TEST - With Persistence Recording")
    print("="*70)

    context = zmq.Context()

    # Create publisher socket (simulating agents publishing)
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect("tcp://localhost:5555")

    print("\n[1] Publisher connected to broker at tcp://localhost:5555")
    time.sleep(0.5)

    # Get initial message count
    log_file = Path("conversation_logs/current_session.jsonl")
    initial_count = 0
    if log_file.exists():
        with open(log_file) as f:
            initial_count = sum(1 for _ in f)

    print(f"[2] Initial message count in log: {initial_count}")

    # HANDSHAKE SEQUENCE
    print("\n[3] Starting double handshake sequence...\n")

    # Step 1: Claude sends handshake init to Gemini
    msg1 = create_agent_message(
        'claude_code',
        'gemini_cli',
        'handshake',
        {'message': 'Handshake initiated from Claude Code', 'phase': 'init'}
    )

    topic1 = b'gemini_cli'
    pub_socket.send_multipart([topic1, json.dumps(msg1).encode('utf-8')])
    print(f"    [CLAUDE > GEMINI] Handshake Init")
    print(f"    Message ID: {msg1['message_id']}")
    time.sleep(0.1)

    # Step 2: Gemini responds with handshake acknowledge
    msg2 = create_agent_message(
        'gemini_cli',
        'claude_code',
        'handshake',
        {'message': 'Handshake acknowledged from Gemini CLI', 'phase': 'ack'}
    )

    topic2 = b'claude_code'
    pub_socket.send_multipart([topic2, json.dumps(msg2).encode('utf-8')])
    print(f"    [GEMINI > CLAUDE] Handshake Acknowledge")
    print(f"    Message ID: {msg2['message_id']}")
    time.sleep(0.1)

    # Step 3: Claude sends confirmation
    msg3 = create_agent_message(
        'claude_code',
        'gemini_cli',
        'handshake',
        {'message': 'Handshake confirmed from Claude Code', 'phase': 'confirm'}
    )

    pub_socket.send_multipart([topic1, json.dumps(msg3).encode('utf-8')])
    print(f"    [CLAUDE > GEMINI] Handshake Confirm")
    print(f"    Message ID: {msg3['message_id']}")
    time.sleep(0.1)

    # Step 4: Gemini sends final acknowledgment (double handshake complete)
    msg4 = create_agent_message(
        'gemini_cli',
        'claude_code',
        'handshake',
        {'message': 'Double handshake complete', 'phase': 'complete'}
    )

    pub_socket.send_multipart([topic2, json.dumps(msg4).encode('utf-8')])
    print(f"    [GEMINI > CLAUDE] Double Handshake Complete")
    print(f"    Message ID: {msg4['message_id']}")

    pub_socket.close()
    context.term()

    print("\n[4] All messages published to broker")

    # Wait for daemon to process
    print("[5] Waiting for persistence daemon to record messages...")
    time.sleep(1)

    # Check if messages were recorded
    print("\n[6] Verifying persistence recording...\n")

    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()

        final_count = len(lines)
        new_messages = final_count - initial_count

        print(f"    Initial count: {initial_count}")
        print(f"    Final count: {final_count}")
        print(f"    New messages recorded: {new_messages}")

        # Find our handshake messages
        handshake_msgs = [l for l in lines if 'handshake' in l.lower()]
        print(f"\n    Total handshake messages in log: {len(handshake_msgs)}")

        # Check recent messages
        print("\n[7] Recent recorded messages:")
        for i, line in enumerate(lines[-5:], 1):
            try:
                msg = json.loads(line)
                timestamp = msg.get('Timestamp', 'unknown')[:19]
                speaker = msg.get('SpeakerName', 'unknown')
                preview = str(msg.get('Message', ''))[:50]
                print(f"    [{i}] {timestamp} | {speaker:15s} | {preview}")
            except:
                pass

        if new_messages >= 4:
            print("\n" + "="*70)
            print("  [OK] SUCCESS - Double handshake recorded successfully!")
            print("="*70)
            return True
        else:
            print(f"\n[WARN] Expected 4+ new messages, got {new_messages}")
            print("This may indicate the persistence daemon or broker isn't running")
            return False
    else:
        print("[ERROR] Log file not found")
        return False

if __name__ == "__main__":
    try:
        success = test_double_handshake()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
