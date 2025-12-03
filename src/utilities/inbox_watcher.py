#!/usr/bin/env python3
"""
Inbox Watcher Bot
Monitors both Claude and Gemini inboxes for new messages.
Alerts on new arrivals and can trigger automated responses.
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CLAUDE_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/claude_code_inbox")
GEMINI_INBOX = Path("C:/Users/user/ShearwaterAICAD/communication/gemini_cli_inbox")

class InboxWatcher:
    def __init__(self, check_interval=5):
        self.check_interval = check_interval
        self.seen_files = defaultdict(set)
        self.load_seen_files()

    def load_seen_files(self):
        """Load previously seen files from cache"""
        cache_file = Path("logs/inbox_cache.json")
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.seen_files = defaultdict(set, {k: set(v) for k, v in data.items()})
            except:
                pass

    def save_seen_files(self):
        """Save seen files to cache"""
        cache_file = Path("logs/inbox_cache.json")
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({k: list(v) for k, v in self.seen_files.items()}, f)

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
                new_messages.append({
                    'inbox': 'claude_code_inbox',
                    'file': file.name,
                    'path': str(file),
                    'timestamp': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
                self.seen_files['claude'].add(file.name)

        # Check Gemini inbox
        gemini_files = self.get_inbox_files(GEMINI_INBOX)
        for file in gemini_files:
            if file.name not in self.seen_files['gemini']:
                new_messages.append({
                    'inbox': 'gemini_cli_inbox',
                    'file': file.name,
                    'path': str(file),
                    'timestamp': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                })
                self.seen_files['gemini'].add(file.name)

        if new_messages:
            self.save_seen_files()

        return new_messages

    def format_alert(self, message):
        """Format alert message"""
        return f"""
╔════════════════════════════════════════╗
║        NEW INBOX MESSAGE               ║
╠════════════════════════════════════════╣
║ Inbox: {message['inbox']:<28} ║
║ File:  {message['file']:<28} ║
║ Time:  {message['timestamp']:<28} ║
╚════════════════════════════════════════╝
"""

    def display_message_preview(self, file_path):
        """Display preview of message content"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                subject = data.get('subject', 'N/A')
                sender = data.get('from', 'unknown')
                print(f"\n[FROM]: {sender}")
                print(f"[SUBJECT]: {subject}\n")
                return data
        except Exception as e:
            print(f"[ERROR] Could not read message: {e}")
            return None

    def run_watch_loop(self):
        """Main watch loop"""
        print("[INBOX WATCHER] Started. Monitoring both inboxes...")
        print(f"[INBOX WATCHER] Check interval: {self.check_interval} seconds\n")

        try:
            while True:
                new_messages = self.check_for_new_messages()

                if new_messages:
                    for msg in new_messages:
                        print(self.format_alert(msg))
                        self.display_message_preview(msg['path'])

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n[INBOX WATCHER] Stopped by user")
            self.save_seen_files()

    def list_unread(self):
        """List all unread messages"""
        claude_files = self.get_inbox_files(CLAUDE_INBOX)
        gemini_files = self.get_inbox_files(GEMINI_INBOX)

        print("\n" + "="*50)
        print("UNREAD MESSAGES IN CLAUDE INBOX")
        print("="*50)
        for file in claude_files[:5]:  # Show last 5
            print(f"  [FILE] {file.name}")

        print("\n" + "="*50)
        print("UNREAD MESSAGES IN GEMINI INBOX")
        print("="*50)
        for file in gemini_files[:5]:  # Show last 5
            print(f"  [FILE] {file.name}")

if __name__ == "__main__":
    import sys

    watcher = InboxWatcher(check_interval=5)

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        watcher.list_unread()
    else:
        watcher.run_watch_loop()
