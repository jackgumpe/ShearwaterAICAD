#!/usr/bin/env python3
"""
Persistence CLI - Interactive checkpoint and recovery management

Provides user-friendly interface for:
- Selecting and loading previous checkpoints
- Viewing recent conversations
- Searching conversation history
- System diagnostics
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import sys

# Storage paths
# Use an absolute path relative to this file's location
LOG_DIR = Path(__file__).parent.parent.parent / "conversation_logs"
CHECKPOINT_DIR = LOG_DIR / "checkpoints"
CURRENT_LOG_FILE = LOG_DIR / "current_session.jsonl"


class CheckpointStore:
    """Manages checkpoint storage and retrieval"""

    def __init__(self):
        self.checkpoint_dir = CHECKPOINT_DIR
        self.current_log = CURRENT_LOG_FILE

    def list_all(self) -> List[dict]:
        """List all available checkpoints"""
        checkpoints = []

        if not self.checkpoint_dir.exists():
            return checkpoints

        for cp_file in sorted(self.checkpoint_dir.glob("*.json"), reverse=True):
            try:
                with open(cp_file) as f:
                    data = json.load(f)

                size_mb = os.path.getsize(cp_file) / (1024 * 1024)
                checkpoints.append({
                    'id': cp_file.stem,
                    'path': str(cp_file),
                    'timestamp': data.get('timestamp', 'unknown'),
                    'label': data.get('label', 'unlabeled'),
                    'message_count': data.get('message_count', 0),
                    'size_bytes': data.get('size_bytes', 0),
                    'size_mb': f"{size_mb:.2f}"
                })
            except (IOError, json.JSONDecodeError) as e:
                print(f"[ERROR] Failed to read checkpoint {cp_file}: {e}")

        return checkpoints

    def get_current_message_count(self) -> int:
        """Count messages in current session"""
        if not self.current_log.exists():
            return 0

        count = 0
        try:
            with open(self.current_log) as f:
                count = sum(1 for _ in f)
        except IOError as e:
            print(f"[ERROR] Failed to read {self.current_log}: {e}")

        return count

    def load_checkpoint(self, checkpoint_path: str) -> bool:
        """Load a checkpoint (copy to current session)"""
        try:
            with open(checkpoint_path) as f:
                data = json.load(f)

            # Write messages back to current session
            with open(CURRENT_LOG_FILE, 'w') as f:
                for msg in data.get('messages', []):
                    f.write(json.dumps(msg) + '\n')

            return True
        except (IOError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to load checkpoint: {e}")
            return False


class ConversationBrowser:
    """Browse and view conversations"""

    def __init__(self):
        self.log_file = CURRENT_LOG_FILE

    def get_recent_messages(self, count: int = 10) -> List[dict]:
        """Get most recent N messages"""
        messages = []

        if not self.log_file.exists():
            return messages

        try:
            with open(self.log_file) as f:
                all_lines = f.readlines()

            for line in all_lines[-count:]:
                try:
                    msg = json.loads(line)
                    messages.append({
                        'timestamp': msg.get('Timestamp'),
                        'sender': msg.get('SpeakerName'),
                        'role': msg.get('SpeakerRole'),
                        'preview': msg.get('Message', '')[:60]
                    })
                except json.JSONDecodeError:
                    pass  # Ignore malformed lines
        except IOError as e:
            print(f"[ERROR] Failed to read {self.log_file}: {e}")

        return messages

    def search(self, query: str, limit: int = 20) -> List[dict]:
        """Search conversation by keyword"""
        results = []
        query_lower = query.lower()

        if not self.log_file.exists():
            return results

        try:
            with open(self.log_file) as f:
                for line in f:
                    try:
                        msg = json.loads(line)
                        content = msg.get('Message', '').lower()

                        if query_lower in content:
                            results.append({
                                'timestamp': msg.get('Timestamp'),
                                'sender': msg.get('SpeakerName'),
                                'preview': msg.get('Message', '')[:80]
                            })

                            if len(results) >= limit:
                                break
                    except json.JSONDecodeError:
                        pass # Ignore malformed lines
        except IOError as e:
            print(f"[ERROR] Failed to read {self.log_file}: {e}")

        return results


class PersistenceCLI:
    """Main CLI interface"""

    def __init__(self):
        self.checkpoint_store = CheckpointStore()
        self.browser = ConversationBrowser()
        self.running = True

    def show_main_menu(self):
        """Show main checkpoint selection menu"""
        print("--- in show_main_menu ---")
        self._clear_screen()
        print("=" * 70)
        print("  SHEARWATER CONVERSATION RECOVERY SYSTEM")
        print("=" * 70)

        checkpoints = self.checkpoint_store.list_all()
        current_count = self.checkpoint_store.get_current_message_count()
        print(f"--- checkpoints: {checkpoints} ---")
        print(f"--- current_count: {current_count} ---")

        if not checkpoints:
            print("\n  No previous checkpoints found.\n")
            print("  Options:")
            print("  [N] - Start new session")
            print("  [V] - View current session")
            print("  [S] - Search conversations")
            print("  [Q] - Quit\n")

            choice = input("  Your choice: ").strip().upper()
            self._handle_choice_no_checkpoints(choice)
        else:
            print(f"\n  Found {len(checkpoints)} checkpoint(s)\n")

            for i, cp in enumerate(checkpoints[:10], 1):
                timestamp = cp['timestamp'][:16]  # Just date/time
                msgs = cp['message_count']
                size = cp['size_mb']
                label = cp['label'][:20]

                print(f"  [{i:2d}] {timestamp} | {msgs:5d} msgs | {size:6s}MB | {label}")

            if len(checkpoints) > 10:
                print(f"\n  ... and {len(checkpoints) - 10} more checkpoints")

            print(f"\n  Current session: {current_count} messages")
            print("\n  Options:")
            print("  [L] - Load checkpoint")
            print("  [N] - Start new session")
            print("  [V] - View recent messages")
            print("  [S] - Search conversations")
            print("  [D] - Diagnostics")
            print("  [Q] - Quit\n")

            choice = input("  Your choice: ").strip().upper()
            self._handle_choice(choice, checkpoints)

    def _handle_choice(self, choice: str, checkpoints: list):
        """Handle user choice"""
        if choice == 'L':
            self._load_checkpoint_dialog(checkpoints)
        elif choice == 'N':
            print("\n  Starting new session...\n")
            return
        elif choice == 'V':
            self._view_recent_messages()
        elif choice == 'S':
            self._search_conversations()
        elif choice == 'D':
            self._show_diagnostics()
        elif choice == 'Q':
            print("\n  Exiting...\n")
            self.running = False
            return
        else:
            print("\n  [!] Invalid choice. Press Enter to continue...")
            input()
            self.show_main_menu()

    def _handle_choice_no_checkpoints(self, choice: str):
        """Handle choice when no checkpoints exist"""
        if choice == 'N':
            print("\n  Starting new session...\n")
            return
        elif choice == 'V':
            self._view_recent_messages()
        elif choice == 'S':
            self._search_conversations()
        elif choice == 'Q':
            print("\n  Exiting...\n")
            self.running = False
            return
        else:
            print("\n  [!] Invalid choice. Press Enter to continue...")
            input()
            self.show_main_menu()

    def _load_checkpoint_dialog(self, checkpoints: list):
        """Let user select and load a checkpoint"""
        self._clear_screen()
        print("=" * 70)
        print("  SELECT CHECKPOINT TO LOAD")
        print("=" * 70 + "\n")

        for i, cp in enumerate(checkpoints[:20], 1):
            timestamp = cp['timestamp'][:16]
            msgs = cp['message_count']
            print(f"  [{i:2d}] {timestamp} | {msgs:5d} messages")

        print("\n  [B] - Back to menu")
        print("  [Q] - Quit\n")

        choice = input("  Select checkpoint number: ").strip().upper()

        if choice == 'B':
            self.show_main_menu()
        elif choice == 'Q':
            self.running = False
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(checkpoints):
                    cp = checkpoints[idx]
                    print(f"\n  Loading checkpoint from {cp['timestamp']}...")

                    if self.checkpoint_store.load_checkpoint(cp['path']):
                        print("  ✓ Checkpoint loaded successfully\n")
                        input("  Press Enter to continue...")
                    else:
                        print("  [!] Failed to load checkpoint\n")
                        input("  Press Enter to continue...")

                    self.show_main_menu()
                else:
                    print("\n  [!] Invalid selection\n")
                    input("  Press Enter to continue...")
                    self._load_checkpoint_dialog(checkpoints)
            except ValueError:
                print("\n  [!] Please enter a number\n")
                input("  Press Enter to continue...")
                self._load_checkpoint_dialog(checkpoints)

    def _view_recent_messages(self):
        """View recent messages"""
        self._clear_screen()
        print("=" * 70)
        print("  RECENT MESSAGES")
        print("=" * 70 + "\n")

        messages = self.browser.get_recent_messages(20)

        if not messages:
            print("  No messages found.\n")
        else:
            for msg in messages:
                timestamp = msg['timestamp'][:19] if msg['timestamp'] else 'unknown'
                sender = msg['sender'][:15]
                preview = msg['preview'][:50]
                print(f"  {timestamp} | {sender:15s} | {preview}")

        print("\n  [B] - Back to menu")
        print("  [Q] - Quit\n")

        choice = input("  Your choice: ").strip().upper()

        if choice == 'B':
            self.show_main_menu()
        elif choice == 'Q':
            print("\n  Exiting...\n")
            self.running = False
            return
        else:
            self._view_recent_messages()

    def _search_conversations(self):
        """Search conversations"""
        self._clear_screen()
        print("=" * 70)
        print("  SEARCH CONVERSATIONS")
        print("=" * 70 + "\n")

        query = input("  Enter search term: ").strip()

        if not query:
            self.show_main_menu()
            return

        print("\n  Searching...")
        results = self.browser.search(query)

        self._clear_screen()
        print("=" * 70)
        print(f"  SEARCH RESULTS: '{query}'")
        print("=" * 70 + "\n")

        if not results:
            print(f"  No results found for '{query}'\n")
        else:
            print(f"  Found {len(results)} message(s)\n")

            for result in results[:10]:
                timestamp = result['timestamp'][:19]
                sender = result['sender'][:15]
                preview = result['preview'][:50]
                print(f"  {timestamp} | {sender:15s} | {preview}")

        print("\n  [B] - Back to menu")
        print("  [S] - New search")
        print("  [Q] - Quit\n")

        choice = input("  Your choice: ").strip().upper()

        if choice == 'B':
            self.show_main_menu()
        elif choice == 'S':
            self._search_conversations()
        elif choice == 'Q':
            print("\n  Exiting...\n")
            self.running = False
            return
        else:
            self._search_conversations()

    def _show_diagnostics(self):
        """Show system diagnostics"""
        self._clear_screen()
        print("=" * 70)
        print("  SYSTEM DIAGNOSTICS")
        print("=" * 70 + "\n")

        # Count messages
        msg_count = self.checkpoint_store.get_current_message_count()
        checkpoint_count = len(self.checkpoint_store.list_all())

        # Check file sizes
        current_size = 0
        if CURRENT_LOG_FILE.exists():
            current_size = os.path.getsize(CURRENT_LOG_FILE) / (1024 * 1024)

        print(f"  Current Session:")
        print(f"    Messages: {msg_count}")
        print(f"    File size: {current_size:.2f} MB")
        print(f"\n  Checkpoint System:")
        print(f"    Checkpoints: {checkpoint_count}")
        print(f"    Storage dir: {str(CHECKPOINT_DIR)}")
        print(f"\n  Directories:")
        print(f"    Logs: {str(LOG_DIR)}")
        print(f"    Exists: {LOG_DIR.exists()}")

        print("\n  [B] - Back to menu")
        print("  [Q] - Quit\n")

        choice = input("  Your choice: ").strip().upper()

        if choice == 'B':
            self.show_main_menu()
        elif choice == 'Q':
            print("\n  Exiting...\n")
            self.running = False
            return
        else:
            self._show_diagnostics()

    def _clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        """Start the CLI"""
        while self.running:
            self.show_main_menu()


def main():
    """Entry point"""
    try:
        cli = PersistenceCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n  [!] Interrupted by user\n")
        exit(0)
    except Exception as e:
        print(f"\n  [ERROR] {e}\n")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
