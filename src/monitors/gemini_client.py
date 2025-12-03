import argparse
import os
from typing import Dict # Added Dict import
import time # Added time import
from core.clients.agent_base_client import AgentBaseClient
from monitors.gemini_api_engine import GeminiApiEngine

# Configuration
GEMINI_AGENT_ID = "gemini_cli"

class GeminiClient(AgentBaseClient):
    """
    Gemini's client implementation for the Synaptic Core (PUB-SUB).
    """
    def __init__(self, api_key: str, num_messages: int = 10, model_name: str = "gemini-pro"):
        # Initialize the base class with the agent's name.
        super().__init__(
            agent_name=GEMINI_AGENT_ID,
            broker_host="localhost",
            pub_port=5555,
            sub_port=5556
        )
        
        # Inject the API key into the engine
        if not api_key:
            raise ValueError("API key must be provided to GeminiClient.")
        self.engine = GeminiApiEngine(api_key=api_key, num_messages=num_messages, model_name=model_name) # Pass num_messages and model_name

    def run(self):
        """
        The main run loop for the Gemini client.
        """
        if not self.connect():
            self.logger.fatal("Could not connect to the Synaptic Core. Exiting.")
            return

        self.logger.info(f"[{self.agent_name}] Entering main loop. Press Ctrl+C to stop.")
        
        try:
            while True:
                # The base class's receive_message will call our hook
                self.receive_message(timeout_ms=1000)
                
                # We can add other idle tasks here if needed in the future

        except KeyboardInterrupt:
            self.logger.info("User interrupt detected. Shutting down.")

    def process_incoming_message(self, message: Dict) -> None:
        """
        Overrides the base class method to provide Gemini-specific logic
        based on the agent interaction protocol.
        """
        if not message:
            return

        sender = message.get("from", "unknown")
        message_type = message.get("type", "unknown")
        message_text = message.get("content", {}).get("message", "")
        self.logger.info(f"Processing message from {sender} (type: {message_type})...")

        # Implement protocol logic
        if message_type == "request":
            self.logger.info(f"Generating response to request from {sender}...")
            try:
                # Generate response using the API engine
                response_text = self.engine.generate_response(message_text)
                self.logger.info(f"Generated response: {response_text[:50]}...")
                
                # Send the engine's response back into the system for logging/observation
                self.send_message("claude_code", "engine_response", {"message": response_text})

            except Exception as e:
                self.logger.error(f"Failed to generate or send response: {e}", exc_info=True)
        
        elif message_type in ["response", "inform", "handshake"]:
             # For responses, informational messages, or handshakes, just log and do nothing.
             self.logger.info(f"Acknowledged '{message_type}' from {sender}.")
        
        else:
            # Handle unknown message types
            self.logger.warning(f"Received unknown message type '{message_type}' from {sender}. Ignoring.")

    def cleanup(self):
        """Saves history and disconnects."""
        self.logger.info("Cleaning up and saving message history...")
        self.save_message_history()
        self.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Gemini client.")
    parser.add_argument("--api-key", required=True, help="The Google Gemini API key.")
    parser.add_argument("--num-messages", type=int, default=10, help="Number of recent messages to include in context.")
    parser.add_argument("--model-name", type=str, default="gemini-pro", help="The Gemini model to use.")
    args = parser.parse_args()
    
    gemini_client = GeminiClient(api_key=args.api_key, num_messages=args.num_messages, model_name=args.model_name)
    gemini_client.run()