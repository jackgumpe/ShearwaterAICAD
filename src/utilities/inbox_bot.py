#!/usr/bin/env python3
"""
Inbox Bot - Automated message monitoring and response system
Can be extended with custom handlers for different message types.
Currently monitors and alerts on new messages.
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import threading

CLAUDE_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox")
GEMINI_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox")
LOGS_DIR = Path("logs")

class InboxBot:
    def __init__(self, check_interval=3, auto_respond=False):
        self.check_interval = check_interval
        self.auto_respond = auto_respond
        self.seen_files = defaultdict(set)
        self.running = True
        self.message_handlers = {}
        self.load_seen_files()
        self.register_default_handlers()

    def register_handler(self, message_type, handler_func):
        """Register a custom handler for a message type"""
        self.message_handlers[message_type] = handler_func

    def register_default_handlers(self):
        """Register default handlers for common message types"""
        self.register_handler("decision_request", self.handle_decision_request)
        self.register_handler("proposal", self.handle_proposal)
        self.register_handler("question", self.handle_question)
        self.register_handler("status", self.handle_status)

    def handle_decision_request(self, message_data):
        """Handle decision request messages"""
        print(f"\n[DECISION REQUIRED]")
        print(f"   From: {message_data.get('from')}")
        print(f"   Subject: {message_data.get('subject')}")

    def handle_proposal(self, message_data):
        """Handle proposal messages"""
        print(f"\n[PROPOSAL RECEIVED]")
        print(f"   From: {message_data.get('from')}")
        print(f"   Subject: {message_data.get('subject')}")

    def handle_question(self, message_data):
        """Handle question messages"""
        print(f"\n[QUESTION RECEIVED]")
        print(f"   From: {message_data.get('from')}")
        print(f"   Subject: {message_data.get('subject')}")

    def handle_status(self, message_data):
        """Handle status messages"""
        print(f"\n[STATUS UPDATE]")
        print(f"   From: {message_data.get('from')}")
        print(f"   Subject: {message_data.get('subject')}")

    def load_seen_files(self):
        """Load previously seen files from cache"""
        cache_file = LOGS_DIR / "inbox_bot_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.seen_files = defaultdict(set, {k: set(v) for k, v in data.items()})
            except:
                pass

    def save_seen_files(self):
        """Save seen files to cache"""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cache_file = LOGS_DIR / "inbox_bot_cache.json"
        with open(cache_file, 'w') as f:
            json.dump({k: list(v) for k, v in self.seen_files.items()}, f)

    def log_message(self, message_data, inbox_name):
        """Log message to inbox bot log"""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / "inbox_bot.log"

        with open(log_file, 'a') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"\n[{timestamp}] {inbox_name}\n")
            f.write(f"  From: {message_data.get('from', 'unknown')}\n")
            f.write(f"  Subject: {message_data.get('subject', 'N/A')}\n")
            f.write(f"  Type: {message_data.get('type', 'unknown')}\n")

    def get_inbox_files(self, inbox_path):
        """Get all JSON files in inbox"""
        if not inbox_path.exists():
            return []
        return sorted([f for f in inbox_path.glob("*.json")], key=lambda x: x.stat().st_mtime, reverse=True)

    def check_for_new_messages(self):
        """Check both inboxes for new files"""
        new_messages = []

        # Check Claude inbox
        claude_files = self.get_inbox_files(CLAUDE_INBOX)
        for file in claude_files:
            if file.name not in self.seen_files['claude']:
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    new_messages.append({
                        'inbox': 'claude_code_inbox',
                        'file': file.name,
                        'path': str(file),
                        'timestamp': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                        'data': data
                    })
                    self.seen_files['claude'].add(file.name)
                except:
                    pass

        # Check Gemini inbox
        gemini_files = self.get_inbox_files(GEMINI_INBOX)
        for file in gemini_files:
            if file.name not in self.seen_files['gemini']:
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    new_messages.append({
                        'inbox': 'gemini_cli_inbox',
                        'file': file.name,
                        'path': str(file),
                        'timestamp': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                        'data': data
                    })
                    self.seen_files['gemini'].add(file.name)
                except:
                    pass

        if new_messages:
            self.save_seen_files()

        return new_messages

    def process_message(self, message):
        """Process a single message"""
        data = message['data']
        message_type = data.get('type', 'unknown')
        inbox_name = message['inbox']

        # Log the message
        self.log_message(data, inbox_name)

        # Call appropriate handler
        if message_type in self.message_handlers:
            self.message_handlers[message_type](data)
        else:
            print(f"\n[NEW MESSAGE] in {inbox_name}")
            print(f"   From: {data.get('from', 'unknown')}")
            print(f"   Subject: {data.get('subject', 'N/A')}\n")

    def run(self):
        """Main bot loop"""
        print("\n" + "="*50)
        print("[INBOX BOT] Started")
        print("="*50)
        print(f"[*] Monitoring Claude and Gemini inboxes")
        print(f"[*] Check interval: {self.check_interval} seconds")
        print(f"[*] Auto-respond enabled: {self.auto_respond}\n")

        try:
            while self.running:
                new_messages = self.check_for_new_messages()

                if new_messages:
                    for msg in new_messages:
                        self.process_message(msg)

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n[INBOX BOT] Stopped by user")
            self.save_seen_files()
        except Exception as e:
            print(f"\n[ERROR] {e}")
            self.save_seen_files()

    def stop(self):
        """Stop the bot"""
        self.running = False

if __name__ == "__main__":
    import sys

    # Create bot
    auto_respond = "--auto" in sys.argv
    bot = InboxBot(check_interval=3, auto_respond=auto_respond)

    # Run
    bot.run()
