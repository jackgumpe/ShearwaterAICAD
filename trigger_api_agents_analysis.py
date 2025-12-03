#!/usr/bin/env python3
"""
Trigger API agents (Claude + Gemini) to review and analyze token optimization reports
"""

import json
import zmq
from datetime import datetime

def send_analysis_request():
    """Send request to broker for API agents to review token analysis"""

    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://127.0.0.1:5555")

    message = {
        "timestamp": datetime.now().isoformat(),
        "sender": "claude_code",
        "recipients": ["claude_api_agent", "gemini_api_agent"],
        "topic": "claude_code",
        "message_type": "analysis_task",
        "priority": "HIGH",
        "subject": "API Agents: Review and Improve Token Optimization Analysis",
        "content": """
You have been assigned a critical analysis task:

TASK: Review the token cost optimization analysis and suggest improvements

The live API agents (you two) have unique insight into:
- Real query patterns and cache hit rates
- Actual edge cases that break assumptions
- Hidden token costs (retries, error handling)
- Which optimizations matter most for real workloads

FILES TO EXAMINE:
1. API_AGENTS_TOKEN_OPTIMIZATION_REPORT.md
2. week2_work/outputs/token_cost_analysis_report.txt
3. week2_work/outputs/token_cost_analysis_simple.json
4. src/monitors/gemini_api_engine.py (cache implementation)
5. GEMINI_CACHING_VERIFICATION_COMPLETE.md

DIALOGUE PROMPT:
See communication/claude_code_inbox/api_agents_analysis_dialogue_start.txt

KEY DEBATES TO HAVE:
1. Are cache hit rates realistic (15-35%)?
2. What accuracy edge cases did we miss?
3. Hidden token costs (retries, errors)?
4. Priority: Concise prompting vs model selection?
5. Multi-process cache coherency?
6. How to verify accuracy in production?

DELIVERABLES (Write to communication/claude_code_inbox/api_agents_token_analysis_dialogue.json):
- Joint analysis and debate
- Accuracy audit plan
- Realistic cache hit rate assessment
- Optimization priority roadmap
- Risk/edge case analysis

This is your expertise. We need your rigorous analysis before we declare this optimization complete.

Ready?
""",
        "attachment": {
            "files": [
                "API_AGENTS_TOKEN_OPTIMIZATION_REPORT.md",
                "week2_work/outputs/token_cost_analysis_report.txt",
                "communication/claude_code_inbox/api_agents_analysis_dialogue_start.txt"
            ],
            "deadline": "ASAP - No strict time limit",
            "importance": "Critical for validating optimization strategy"
        }
    }

    # Send message
    socket.send_json(message)
    print(f"[SENT] Analysis task to API agents")
    print(f"       Timestamp: {message['timestamp']}")
    print(f"       Priority: {message['priority']}")
    print(f"       Subject: {message['subject']}")

    socket.close()
    context.term()

if __name__ == "__main__":
    try:
        send_analysis_request()
        print("\n[OK] Analysis request transmitted to API agents")
        print("     They will begin examining the reports and debating findings")
        print("     Watch communication/claude_code_inbox/ for their dialogue output")
    except Exception as e:
        print(f"[ERROR] Failed to send: {e}")
        print("        Make sure broker is running (python manage.py start)")
