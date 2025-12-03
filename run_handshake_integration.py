"""Test triple handshake - basic agent collaboration"""
import sys
import os
import time
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.pm_alpha import PMAlpha
from agents.pm_beta import PMBeta
from core.database import init_db, Conversation
from core.message_bus import MessageBus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_triple_handshake():
    """Test basic agent initialization and communication"""
    print("=" * 60)
    print("SHEARWATER AICAD - Triple Handshake Test")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database...")
    db = init_db()
    print("   ✓ Database initialized")

    # Get API keys
    anthropic_key = "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" # TEMP WORKAROUND
    openai_key = "YOUR_OPENAI_API_KEY" # TEMP WORKAROUND - Replace with your actual key

    if not anthropic_key or not openai_key:
        print("\n   ✗ API keys not found in .env file")
        print("   Please set ANTHROPIC_API_KEY and OPENAI_API_KEY")
        return False

    # Create a shared message bus
    message_bus = MessageBus("handshake_test")

    # Create agents
    print("\n2. Creating agents...")
    try:
        pm_alpha = PMAlpha(db, anthropic_key, message_bus)
        print("   ✓ PM-Alpha (The Architect) initialized")

        pm_beta = PMBeta(db, openai_key, message_bus)
        print("   ✓ PM-Beta (The Executor) initialized")
    except Exception as e:
        print(f"   ✗ Error creating agents: {e}")
        return False

    # Start agents
    print("\n3. Starting agents...")
    pm_alpha.start()
    print("   ✓ PM-Alpha listening")
    pm_beta.start()
    print("   ✓ PM-Beta listening")

    # Test task processing
    print("\n4. Testing task processing...")
    test_task = {
        "id": "test_001",
        "description": "Design the triple agent architecture for ShearwaterAICAD"
    }

    try:
        result = pm_alpha.process_task(test_task)
        print("   ✓ PM-Alpha processed task")
        print(f"   Result preview: {result[:100]}...")
    except Exception as e:
        print(f"   ✗ Error processing task: {e}")

    # Test opinion formation
    print("\n5. Testing opinion formation...")
    debate_topic = "Should we prioritize database optimization or feature development?"

    try:
        alpha_opinion = pm_alpha.formulate_opinion(debate_topic)
        print("   ✓ PM-Alpha formed opinion")
        print(f"   Opinion preview: {alpha_opinion[:80]}...")

        beta_opinion = pm_beta.formulate_opinion(debate_topic)
        print("   ✓ PM-Beta formed opinion")
        print(f"   Opinion preview: {beta_opinion[:80]}...")
    except Exception as e:
        print(f"   ✗ Error forming opinions: {e}")

    # Check database
    print("\n6. Checking database...")
    conversations = db.query(Conversation).all()
    print(f"   ✓ Database entries: {len(conversations)}")

    # Summary
    print("\n" + "=" * 60)
    print("Triple Handshake Test Summary")
    print("=" * 60)
    print(f"Agents created: 2 (PM-Alpha, PM-Beta)")
    print(f"Database entries: {len(conversations)}")
    print(f"Status: {'READY FOR PHASE 1' if len(conversations) > 0 else 'CHECK LOGS'}")
    print("=" * 60)

    # Stop the shared message bus
    message_bus.stop()

    return True


if __name__ == "__main__":
    test_triple_handshake()
