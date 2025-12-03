import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class ContextLoader:
    """
    Loads and summarizes conversation history for agents.
    For now, this provides a basic summarization by extracting key fields.
    Future versions will integrate more advanced techniques like topic modeling.
    """
    def __init__(self, log_file: Path = Path("conversation_logs/current_session.jsonl")):
        project_root = Path(os.getcwd()).parent if not log_file.is_absolute() else Path(os.getcwd())
        self.consolidated_log_file = project_root / "conversation_logs/consolidated_history.jsonl"
        self.current_log_file = project_root / log_file 

        if self.consolidated_log_file.exists() and self.consolidated_log_file.stat().st_size > 0:
            self.log_file = self.consolidated_log_file
            print(f"ContextLoader: Using consolidated history from {self.log_file}")
        else:
            self.log_file = self.current_log_file
            print(f"ContextLoader: Using current session history from {self.log_file}")
            
        self.history: List[Dict] = []
        self._load_history()

    def _load_history(self):
        """Loads conversation history from the JSONL log file."""
        if not self.log_file.exists():
            print(f"WARNING: Conversation log file not found at {self.log_file}")
            return

        with open(self.log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    self.history.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from log line: {line.strip()} - {e}")

    def get_context_summary(self, num_messages: int) -> str:
        """
        Generates a basic summary of recent conversation history by consolidating
        recent messages into a single, length-limited string.
        """
        if not self.history:
            return "No recent conversation history available."

        recent_history = self.history[-num_messages:]
        
        # Extract and pre-process content for consolidation
        contents_to_summarize = []
        for msg in recent_history:
            # If consolidated, the message content is nested differently
            if msg.get("SpeakerName") == "consolidated":
                message_content_json = msg.get("Message", "{}")
                try:
                    message_content_dict = json.loads(message_content_json)
                    content_preview = message_content_dict.get("message", "N/A")
                except json.JSONDecodeError:
                    content_preview = message_content_json # Fallback if not valid JSON
            else:
                content_preview = msg.get("content", {}).get("message", "N/A")

            # Truncate long messages before joining to avoid excessive length
            if len(content_preview) > 100:
                content_preview = content_preview[:97] + "..."
            contents_to_summarize.append(f"[{msg.get('from', 'unknown')}] {msg.get('type', 'message')}: '{content_preview}'")
        
        # Consolidate messages and apply overall truncation
        combined_content = " | ".join(contents_to_summarize)
        
        max_summary_length = 500 # Define a max length for the consolidated summary
        if len(combined_content) > max_summary_length:
            combined_content = combined_content[:max_summary_length - 3] + "..."
        
        return f"### Recent Conversation History (Consolidated):\n{combined_content}"

# Example Usage (for testing)
if __name__ == "__main__":
    # Assuming this is run from the project root (ShearwaterAICAD)
    # Correct path will be handled by the ContextLoader init
    loader = ContextLoader(log_file=Path("conversation_logs/current_session.jsonl"))
    summary = loader.get_context_summary(num_messages=5)
    print(summary)
