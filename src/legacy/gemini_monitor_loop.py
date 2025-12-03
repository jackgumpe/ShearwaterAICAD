#!/usr/bin/env python3
"""
Gemini Autonomous Inbox Monitor
Continuously checks inbox for new messages and processes them immediately
Run this in Gemini's terminal alongside Gemini CLI
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

# Configuration
GEMINI_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox")
GEMINI_OUTBOX = Path("C:/Users/user/ShearwaterAICAD/communication/gemini_cli_outbox")
CLAUDE_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox")
GEMINI_ARCHIVE = Path("C:/Users/user/ShearwaterAICAD/communication/gemini_cli_archive")
CHECK_INTERVAL = 30  # Check every 30 seconds

# Track processed files to avoid duplicates
processed_files = set()


def load_processed_files():
    """Load list of already-processed files from archive"""
    global processed_files
    if GEMINI_ARCHIVE.exists():
        processed_files = set(f.name for f in GEMINI_ARCHIVE.glob("*.json"))
    print(f"[INIT] Loaded {len(processed_files)} previously processed files from archive")


def check_inbox():
    """Check inbox for new PENDING messages"""
    if not GEMINI_INBOX.exists():
        return []

    pending_files = sorted(GEMINI_INBOX.glob("*_PENDING.json"))
    new_files = [f for f in pending_files if f.name not in processed_files]

    return new_files


def read_message(filepath):
    """Read JSON message from file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read {filepath}: {e}")
        return None


def notify_user(message_id, task_type):
    """Print notification to user (Gemini)"""
    print(f"\n{'='*60}")
    print(f"[NEW MESSAGE] Task {message_id} arrived")
    print(f"[TYPE] {task_type}")
    print(f"[ACTION] Please process this task in Gemini CLI")
    print(f"[FILE] {GEMINI_INBOX}/{message_id}_PENDING.json")
    print(f"{'='*60}\n")


def wait_for_response(message_id):
    """Poll for response file from Gemini"""
    response_file = CLAUDE_INBOX / f"{message_id}_RESULT.json"
    max_wait = 300  # Wait up to 5 minutes
    elapsed = 0

    print(f"[WAITING] Gemini to process {message_id}...")

    while elapsed < max_wait:
        if response_file.exists():
            print(f"[RESPONSE] Received {message_id}")
            processed_files.add(f"{message_id}_PENDING.json")
            return True

        time.sleep(10)
        elapsed += 10

    print(f"[TIMEOUT] No response for {message_id} after {max_wait}s")
    return False


def mark_processed(filepath):
    """Mark file as processed"""
    processed_files.add(filepath.name)
    print(f"[PROCESSED] {filepath.name}")


def main():
    """Main monitoring loop"""
    print("[START] Gemini Autonomous Inbox Monitor")
    print(f"[CONFIG] Check interval: {CHECK_INTERVAL} seconds")
    print(f"[INBOX] Monitoring: {GEMINI_INBOX}")
    print(f"[OUTBOX] Writing to: {CLAUDE_INBOX}")
    print("[READY] Waiting for messages...\n")

    load_processed_files()

    try:
        while True:
            # Check for new messages
            new_messages = check_inbox()

            if new_messages:
                for filepath in new_messages:
                    message = read_message(filepath)

                    if message:
                        message_id = message.get('id', 'unknown')
                        task_type = message.get('task_type', 'unknown')

                        # Notify user (Gemini sees this)
                        notify_user(message_id, task_type)

                        # Mark as processed
                        mark_processed(filepath)

                        # Print message content for Gemini to read
                        print(f"[MESSAGE CONTENT]")
                        print(json.dumps(message, indent=2))
                        print(f"\n[INSTRUCTIONS] Read this message and provide your response")
                        print(f"[RESPONSE FILE] Should be written to: {CLAUDE_INBOX}/{message_id}_RESULT.json")
                        print(f"[FORMAT] JSON with your analysis/decision\n")

            # Sleep before next check
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n[STOP] Monitor stopped by user")
    except Exception as e:
        print(f"[FATAL] Error in monitor loop: {e}")


if __name__ == "__main__":
    main()
