#!/usr/bin/env python3
"""
Claude Code Autonomous Inbox Monitor
Continuously checks inbox for new messages and processes them immediately
This runs autonomously to enable real-time conversation with Gemini
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

# Configuration
CLAUDE_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox")
CLAUDE_OUTBOX = Path("C:/Users/user/ShearwaterAICAD/communication/claude_code_outbox")
GEMINI_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox")
CLAUDE_ARCHIVE = Path("C:/Users/user/ShearwaterAICAD/communication/claude_code_archive")
CHECK_INTERVAL = 10  # Check every 10 seconds (more frequent than Gemini)

# Track processed files
processed_files = set()


def load_processed_files():
    """Load list of already-processed files from archive"""
    global processed_files
    if CLAUDE_ARCHIVE.exists():
        processed_files = set(f.name for f in CLAUDE_ARCHIVE.glob("*.json"))
    print(f"[CLAUDE INIT] Loaded {len(processed_files)} previously processed files from archive")


def check_inbox():
    """Check inbox for new RESULT messages"""
    if not CLAUDE_INBOX.exists():
        return []

    result_files = sorted(CLAUDE_INBOX.glob("*_RESULT.json"))
    new_files = [f for f in result_files if f.name not in processed_files]

    return new_files


def read_message(filepath):
    """Read JSON message from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[CLAUDE ERROR] Failed to read {filepath}: {e}")
        return None


def process_message(message, filepath):
    """Process incoming message from Gemini"""
    message_id = message.get('id', 'unknown')
    sender = message.get('from', 'unknown')
    msg_type = message.get('type', 'unknown')

    print(f"\n{'='*60}")
    print(f"[CLAUDE] Received message from {sender}")
    print(f"[ID] {message_id}")
    print(f"[TYPE] {msg_type}")
    print(f"[TIME] {datetime.now().isoformat()}")
    print(f"{'='*60}")
    print(json.dumps(message.get('content', {}), indent=2))
    print(f"{'='*60}\n")

    # Mark as processed
    processed_files.add(filepath.name)


def main():
    """Main monitoring loop"""
    print("[CLAUDE] Autonomous Inbox Monitor Started")
    print(f"[CONFIG] Check interval: {CHECK_INTERVAL} seconds")
    print(f"[INBOX] Monitoring: {CLAUDE_INBOX}")
    print("[READY] Waiting for responses from Gemini...\n")

    load_processed_files()

    try:
        while True:
            # Check for new messages
            new_messages = check_inbox()

            if new_messages:
                for filepath in new_messages:
                    message = read_message(filepath)

                    if message:
                        process_message(message, filepath)

            # Sleep before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n[CLAUDE] Monitor stopped by user")
    except Exception as e:
        print(f"[CLAUDE FATAL] Error in monitor loop: {e}")


if __name__ == "__main__":
    main()
