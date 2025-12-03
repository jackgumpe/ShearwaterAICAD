#!/usr/bin/env python3
"""
ZeroMQ Conversation Log Viewer

View and query recorded conversations from broker's persistent logs.
Useful for reviewing past conversations or recovering from crashes.

Usage:
    python zmq_log_viewer.py [--limit 50] [--tier A|C|E] [--chain reconstruction]
"""

import json
from pathlib import Path
import argparse
from datetime import datetime

LOG_DIR = Path("conversation_logs")
CURRENT_LOG_FILE = LOG_DIR / "current_session.jsonl"
ARCHIVE_DIR = LOG_DIR / "archive"


def load_logs(file_path):
    """Load all messages from a JSONL log file"""
    messages = []

    if not file_path.exists():
        print(f"[ERROR] Log file not found: {file_path}")
        return messages

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    msg = json.loads(line.strip())
                    messages.append(msg)
                except json.JSONDecodeError as e:
                    print(f"[WARNING] Line {line_num} invalid JSON: {e}")
                    continue

        print(f"[*] Loaded {len(messages)} messages from {file_path}")
        return messages

    except Exception as e:
        print(f"[ERROR] Failed to load log: {e}")
        return []


def filter_messages(messages, tier=None, chain=None, sender=None):
    """Filter messages by tier, chain type, or sender"""
    filtered = messages

    if tier:
        filtered = [m for m in filtered if m.get('tier') == tier]

    if chain:
        filtered = [m for m in filtered if m.get('chain_type') == chain]

    if sender:
        filtered = [m for m in filtered if m.get('sender') == sender]

    return filtered


def display_message(msg, show_content=True):
    """Pretty-print a single message"""
    print(f"\n{'='*80}")
    print(f"[#{msg.get('message_num', '?')}] {msg.get('sender', 'unknown')} → {msg.get('topic', 'unknown')}")
    print(f"[TIME] {msg.get('timestamp', 'unknown')}")
    print(f"[TIER] {msg.get('tier', 'E')} | [CHAIN] {msg.get('chain_type', 'unknown')}")
    print(f"[ID] {msg.get('message_id', 'unknown')}")

    if msg.get('shl_tags'):
        print(f"[SHL] {', '.join(msg['shl_tags'])}")

    if show_content:
        print(f"\n[CONTENT]:")
        if isinstance(msg.get('content'), dict):
            print(json.dumps(msg['content'], indent=2, ensure_ascii=False))
        else:
            print(msg.get('content'))

    print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(description="View ZeroMQ conversation logs")
    parser.add_argument("--limit", type=int, default=50, help="Number of recent messages to show")
    parser.add_argument("--tier", choices=['A', 'C', 'E'], help="Filter by ACE tier")
    parser.add_argument("--chain", help="Filter by domain chain type")
    parser.add_argument("--sender", help="Filter by sender (claude_code, gemini_cli, etc.)")
    parser.add_argument("--archive", help="View archived session (filename in archive/)")
    parser.add_argument("--list-archives", action="store_true", help="List all archived sessions")
    parser.add_argument("--stats", action="store_true", help="Show conversation statistics")
    parser.add_argument("--full", action="store_true", help="Show full content of messages")

    args = parser.parse_args()

    # --- List archives ---
    if args.list_archives:
        print(f"[*] Archived sessions in {ARCHIVE_DIR}:")
        if ARCHIVE_DIR.exists():
            sessions = list(ARCHIVE_DIR.glob("*.jsonl"))
            if sessions:
                for i, session in enumerate(sorted(sessions), 1):
                    size_kb = session.stat().st_size / 1024
                    mtime = datetime.fromtimestamp(session.stat().st_mtime)
                    print(f"  {i}. {session.name} ({size_kb:.1f} KB) - {mtime}")
            else:
                print("  [No archived sessions found]")
        else:
            print("  [Archive directory does not exist]")
        return

    # --- Determine which log file to view ---
    if args.archive:
        log_file = ARCHIVE_DIR / args.archive
        if not log_file.exists():
            # Try without path
            log_file = ARCHIVE_DIR / f"{args.archive}"
            if not log_file.exists():
                print(f"[ERROR] Archive not found: {args.archive}")
                print(f"[TIP] Use --list-archives to see available sessions")
                return
    else:
        log_file = CURRENT_LOG_FILE

    # --- Load messages ---
    messages = load_logs(log_file)

    if not messages:
        print("[WARNING] No messages found")
        return

    # --- Filter messages ---
    filtered = filter_messages(messages, tier=args.tier, chain=args.chain, sender=args.sender)

    print(f"\n[*] Showing {min(args.limit, len(filtered))} of {len(filtered)} messages")

    # --- Show statistics ---
    if args.stats:
        print(f"\n{'='*80}")
        print("[CONVERSATION STATISTICS]")
        print(f"{'='*80}")

        # Tier distribution
        tier_counts = {}
        for msg in filtered:
            tier = msg.get('tier', 'E')
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        print("\n[ACE Tier Distribution]:")
        for tier in ['A', 'C', 'E']:
            count = tier_counts.get(tier, 0)
            pct = (count / len(filtered) * 100) if filtered else 0
            print(f"  {tier}-Tier: {count} messages ({pct:.1f}%)")

        # Chain distribution
        chain_counts = {}
        for msg in filtered:
            chain = msg.get('chain_type', 'unknown')
            chain_counts[chain] = chain_counts.get(chain, 0) + 1

        print("\n[Domain Chains]:")
        for chain in sorted(chain_counts.keys()):
            count = chain_counts[chain]
            print(f"  {chain}: {count} messages")

        # Sender distribution
        sender_counts = {}
        for msg in filtered:
            sender = msg.get('sender', 'unknown')
            sender_counts[sender] = sender_counts.get(sender, 0) + 1

        print("\n[Senders]:")
        for sender in sorted(sender_counts.keys()):
            count = sender_counts[sender]
            print(f"  {sender}: {count} messages")

        print(f"\n[Time Range]:")
        if filtered:
            first_time = filtered[0].get('timestamp', 'unknown')
            last_time = filtered[-1].get('timestamp', 'unknown')
            print(f"  From: {first_time}")
            print(f"  To:   {last_time}")

    # --- Display messages ---
    print(f"\n[RECENT MESSAGES]:\n")

    # Show last N messages
    for msg in filtered[-args.limit:]:
        display_message(msg, show_content=args.full)


if __name__ == "__main__":
    main()
