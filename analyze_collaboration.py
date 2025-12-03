import json
from pathlib import Path

def analyze_collaboration(superthreads_file: str):
    """
    Analyzes the superthreads file to find and summarize collaborative threads
    between claude_code and gemini_cli.
    """
    superthreads_path = Path(superthreads_file)
    if not superthreads_path.exists():
        print(f"Error: Superthreads file not found at {superthreads_path}")
        return

    with open(superthreads_path, 'r', encoding='utf-8') as f:
        superthreads_data = json.load(f)

    print("--- Analysis of Collaborative Threads ---")
    
    found_collaboration = False
    for topic, threads in superthreads_data.items():
        collaborative_threads_in_topic = []
        for thread in threads:
            participants = thread.get('participants', [])
            # Check if both agents are in the conversation
            if 'claude_code' in participants and 'gemini_cli' in participants:
                collaborative_threads_in_topic.append(thread)
                found_collaboration = True

        if collaborative_threads_in_topic:
            print(f"\nSuperthread: {topic}")
            print("-" * (len(topic) + 12))
            for thread in collaborative_threads_in_topic:
                print(f"  - Thread ID: {thread['thread_id']}")
                print(f"    - Message Count: {thread['message_count']}")
                print(f"    - Duration (s): {thread['duration_seconds']:.2f}")
                if thread.get('context_shifts'):
                    print(f"    - Context Shifts Detected: {len(thread['context_shifts'])}")
                    for shift in thread['context_shifts']:
                        print(f"      - From '{shift['from_topic']}' to '{shift['to_topic']}' at message {shift['message_index']}")
    
    if not found_collaboration:
        print("\nNo direct collaborative threads between claude_code and gemini_cli found in the analysis.")

if __name__ == "__main__":
    analyze_collaboration("conversation_logs/superthreads.json")
