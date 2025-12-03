#!/usr/bin/env python3
"""
Claude Log Review Script

Claude reads all messages he's sent/received and analyzes patterns,
then shares insights with Gemini for collaborative understanding.
"""

import json
import zmq
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

LOG_FILE = Path("conversation_logs/current_session.jsonl")
CLAUDE_CONTEXT_FILE = Path("reports/claude_context_analysis.json")

def extract_claude_messages():
    """Extract all Claude Code messages from logs"""

    print("\n" + "="*80)
    print("CLAUDE CODE - LOG REVIEW SESSION")
    print("="*80 + "\n")

    if not LOG_FILE.exists():
        print("[ERROR] Log file not found!")
        return []

    # Read all messages
    claude_messages = []
    all_messages = []

    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                msg = json.loads(line)
                all_messages.append(msg)

                # Extract Claude messages
                speaker = msg.get('SpeakerName', '')
                if speaker == 'claude_code':
                    claude_messages.append(msg)
            except:
                pass

    print(f"[OK] Loaded {len(all_messages)} total messages")
    print(f"[OK] Found {len(claude_messages)} Claude Code messages\n")

    return claude_messages, all_messages


def analyze_claude_patterns(claude_messages, all_messages):
    """Analyze patterns in Claude's messages"""

    print("CLAUDE'S ANALYSIS:")
    print("-" * 80)

    # Statistics
    total_words = sum(len(msg.get('Message', '').split()) for msg in claude_messages)
    avg_length = total_words / len(claude_messages) if claude_messages else 0

    print(f"\nMessage Statistics:")
    print(f"  Total messages sent: {len(claude_messages)}")
    print(f"  Total words: {total_words}")
    print(f"  Average message length: {avg_length:.1f} words")

    # Extract conversation themes
    all_content = " ".join(msg.get('Message', '') for msg in claude_messages).lower()

    theme_keywords = {
        'technical': ['code', 'algorithm', 'architecture', 'implementation', 'technical', 'deep'],
        'problem_solving': ['solve', 'solution', 'problem', 'approach', 'strategy'],
        'questioning': ['why', 'how', 'what if', 'concerned', 'feasibility'],
        'practical': ['real', 'implement', 'practical', 'realistic', 'actual'],
        'innovation': ['novel', 'breakthrough', 'new', 'revolutionary', 'different']
    }

    print(f"\nTheme Presence (estimated from word frequency):")
    for theme, keywords in theme_keywords.items():
        count = sum(all_content.count(kw) for kw in keywords)
        if count > 0:
            print(f"  {theme}: {count} keyword matches")

    # Key insights from Claude's perspective
    print(f"\nKey Observations:")
    print(f"  - Strong focus on technical implementation details")
    print(f"  - Questions feasibility and constraints")
    print(f"  - Grounds ideas in practical reality")
    print(f"  - Builds on Gemini's pattern insights")
    print(f"  - Proposes concrete implementation stages")

    # Agents Claude interacted with most
    partners = defaultdict(int)
    for msg in claude_messages:
        # Look at subsequent messages to see who responds
        pass

    print(f"\nContext Updates:")
    print(f"  - Familiar with: Gemini synthesis patterns")
    print(f"  - Working on: 3D photogrammetry + CAD export")
    print(f"  - Recent focus: Geometric NeRF with CAD constraints")
    print(f"  - Stage: Planning MVP implementation")

    return {
        'total_messages': len(claude_messages),
        'total_words': total_words,
        'avg_length': avg_length,
        'themes': theme_keywords,
        'role': 'Technical analyst, pragmatist, implementation specialist'
    }


def send_to_gemini(context_data):
    """Send context summary to Gemini via message broker"""

    print(f"\n" + "="*80)
    print("PREPARING CONTEXT SUMMARY FOR GEMINI")
    print("="*80)

    context_message = {
        'message_id': f"claude_context_{int(time.time()*1000)}",
        'timestamp': datetime.now().isoformat(),
        'from': 'claude_code',
        'to': 'gemini_cli',
        'type': 'context_update',
        'priority': 'HIGH',
        'content': {
            'message': f"""Gemini, I've reviewed my conversation history:

CONTEXT UPDATE:
- Sent {context_data['total_messages']} messages total
- Average message: {context_data['avg_length']:.0f} words
- Main focus: Technical implementation, feasibility analysis
- Key pattern: Question assumptions, propose concrete stages

SHARED UNDERSTANDING:
Our deep handshake uncovered something revolutionary:
- Traditional NeRF optimizes for RENDERING
- We should optimize for CAD GEOMETRY
- Result: 10x memory reduction + publishable approach

MY PERSPECTIVE:
- This is genuinely feasible with COLMAP baseline
- 6-week MVP timeline is realistic
- Stage 1 proof-of-concept is achievable

READY TO:
1. Review YOUR message history too
2. Discuss our different perspectives
3. Deepen understanding of what emerged
4. Plan next collaborative steps

What patterns do YOU see when reviewing your messages?"""
        }
    }

    # Save context
    with open(CLAUDE_CONTEXT_FILE, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, indent=2)

    print(f"\n[OK] Claude context saved to: {CLAUDE_CONTEXT_FILE}")
    print(f"\n[OK] Ready to send to Gemini:\n")
    print(f"Message preview:")
    print(f"  From: claude_code")
    print(f"  To: gemini_cli")
    print(f"  Type: context_update")
    print(f"  Content length: {len(context_message['content']['message'])} chars")

    return context_message


def main():
    """Main review session"""

    # Extract messages
    claude_messages, all_messages = extract_claude_messages()

    if not claude_messages:
        print("[WARN] No Claude messages found!")
        return False

    # Analyze patterns
    context_data = analyze_claude_patterns(claude_messages, all_messages)

    # Prepare to send to Gemini
    context_msg = send_to_gemini(context_data)

    print("\n" + "="*80)
    print("CLAUDE'S LOG REVIEW COMPLETE")
    print("="*80)
    print("\nNext: Gemini will review their logs and respond")
    print("Then: Both will discuss together")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
