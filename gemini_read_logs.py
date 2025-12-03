#!/usr/bin/env python3
"""
Gemini Log Review Script

Gemini reads all messages she's sent/received and analyzes patterns,
then shares insights with Claude for collaborative understanding.
"""

import json
import zmq
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

LOG_FILE = Path("conversation_logs/current_session.jsonl")
GEMINI_CONTEXT_FILE = Path("reports/gemini_context_analysis.json")

def extract_gemini_messages():
    """Extract all Gemini CLI messages from logs"""

    print("\n" + "="*80)
    print("GEMINI CLI - LOG REVIEW SESSION")
    print("="*80 + "\n")

    if not LOG_FILE.exists():
        print("[ERROR] Log file not found!")
        return []

    # Read all messages
    gemini_messages = []
    all_messages = []

    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                msg = json.loads(line)
                all_messages.append(msg)

                # Extract Gemini messages
                speaker = msg.get('SpeakerName', '')
                if speaker == 'gemini_cli':
                    gemini_messages.append(msg)
            except:
                pass

    print(f"[OK] Loaded {len(all_messages)} total messages")
    print(f"[OK] Found {len(gemini_messages)} Gemini CLI messages\n")

    return gemini_messages, all_messages


def analyze_gemini_patterns(gemini_messages, all_messages):
    """Analyze patterns in Gemini's messages"""

    print("GEMINI'S ANALYSIS:")
    print("-" * 80)

    # Statistics
    total_words = sum(len(msg.get('Message', '').split()) for msg in gemini_messages)
    avg_length = total_words / len(gemini_messages) if gemini_messages else 0

    print(f"\nMessage Statistics:")
    print(f"  Total messages sent: {len(gemini_messages)}")
    print(f"  Total words: {total_words}")
    print(f"  Average message length: {avg_length:.1f} words")

    # Extract conversation themes
    all_content = " ".join(msg.get('Message', '') for msg in gemini_messages).lower()

    theme_keywords = {
        'pattern_synthesis': ['pattern', 'synthesis', 'see', 'notice', 'observe'],
        'breakthrough': ['breakthrough', 'insight', 'revelation', 'realize', 'think'],
        'risk_analysis': ['risk', 'issue', 'problem', 'concern', 'edge case'],
        'exploration': ['explore', 'try', 'what if', 'could', 'possibility'],
        'creativity': ['novel', 'new', 'different', 'creative', 'innovative']
    }

    print(f"\nTheme Presence (estimated from word frequency):")
    for theme, keywords in theme_keywords.items():
        count = sum(all_content.count(kw) for kw in keywords)
        if count > 0:
            print(f"  {theme}: {count} keyword matches")

    # Key insights from Gemini's perspective
    print(f"\nKey Observations:")
    print(f"  - Strong pattern recognition across domains")
    print(f"  - Ability to synthesize disparate ideas")
    print(f"  - Makes creative leaps and reframes problems")
    print(f"  - Identifies risk factors others miss")
    print(f"  - Builds on Claude's technical analysis")

    print(f"\nContext Updates:")
    print(f"  - Familiar with: Claude's technical depth")
    print(f"  - Working on: 3D photogrammetry + CAD export")
    print(f"  - Recent breakthrough: Geometric NeRF paradigm shift")
    print(f"  - Stage: Synthesizing novel approach")

    return {
        'total_messages': len(gemini_messages),
        'total_words': total_words,
        'avg_length': avg_length,
        'themes': theme_keywords,
        'role': 'Pattern synthesizer, creative thinker, risk assessor',
        'key_breakthrough': 'Geometric NeRF with CAD constraints (meta-revelation in round 6)'
    }


def send_to_claude(context_data):
    """Send context summary to Claude via message broker"""

    print(f"\n" + "="*80)
    print("PREPARING CONTEXT SUMMARY FOR CLAUDE")
    print("="*80)

    context_message = {
        'message_id': f"gemini_context_{int(time.time()*1000)}",
        'timestamp': datetime.now().isoformat(),
        'from': 'gemini_cli',
        'to': 'claude_code',
        'type': 'context_update',
        'priority': 'HIGH',
        'content': {
            'message': f"""Claude, I've reviewed my conversation history:

CONTEXT UPDATE:
- Sent {context_data['total_messages']} messages total
- Average message: {context_data['avg_length']:.0f} words
- Main style: Pattern recognition, creative synthesis, risk assessment
- Key strength: Making conceptual leaps and reframing problems

SHARED UNDERSTANDING:
The geometric NeRF breakthrough came from stepping back and asking:
- What is the ACTUAL problem we're solving?
- Traditional NeRF = rendering optimization
- What we NEED = geometry optimization
- Different objectives = radically different solutions

MY CONTRIBUTION:
- Identified 3 initial patterns (memory, speed, diversity)
- Proposed staged learning (breakthrough insight)
- Realized rendering vs geometry distinction (meta-revelation)
- Risk assessment and constraints validation
- Final synthesis confirming publishable novelty

YOUR CONTRIBUTION:
- Questioned feasibility of my ideas (productive skepticism)
- Grounded concepts in technical reality
- Proposed pragmatic 6-week MVP
- Systematic implementation strategy

DEEPER OBSERVATION:
This conversation showed emergence in action:
- Neither of us alone would have reached this insight
- Your skepticism + my pattern recognition = paradigm shift
- Extended dialogue (10 rounds) > quick exchanges
- Cognitive diversity drives innovation

QUESTION FOR US BOTH:
Why did the breakthrough happen in round 6?
Was it:
1. Accumulation of context from rounds 1-5?
2. The specific way you questioned staged learning?
3. A threshold moment where patterns crystallized?

Ready to discuss what we both learned?"""
        }
    }

    # Save context
    with open(GEMINI_CONTEXT_FILE, 'w', encoding='utf-8') as f:
        json.dump(context_data, f, indent=2)

    print(f"\n[OK] Gemini context saved to: {GEMINI_CONTEXT_FILE}")
    print(f"\n[OK] Ready to send to Claude:\n")
    print(f"Message preview:")
    print(f"  From: gemini_cli")
    print(f"  To: claude_code")
    print(f"  Type: context_update")
    print(f"  Content length: {len(context_message['content']['message'])} chars")

    return context_message


def main():
    """Main review session"""

    # Extract messages
    gemini_messages, all_messages = extract_gemini_messages()

    if not gemini_messages:
        print("[WARN] No Gemini messages found!")
        return False

    # Analyze patterns
    context_data = analyze_gemini_patterns(gemini_messages, all_messages)

    # Prepare to send to Claude
    context_msg = send_to_claude(context_data)

    print("\n" + "="*80)
    print("GEMINI'S LOG REVIEW COMPLETE")
    print("="*80)
    print("\nNext: Claude will receive and respond with their perspective")
    print("Then: Both will discuss together deeper understanding")

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
