import argparse
import os
from typing import Dict # Added Dict import
from core.clients.agent_base_client import AgentBaseClient
from monitors.claude_api_engine import ClaudeApiEngine

# Configuration
CLAUDE_AGENT_ID = "claude_code"

class ClaudeClient(AgentBaseClient):
    """
    Claude's client implementation for the Synaptic Core (PUB-SUB).
    """
    def __init__(self, api_key: str, model_name: str = "claude-3-haiku-20240307"):
        # Initialize the base class with the agent's name.
        super().__init__(
            agent_name=CLAUDE_AGENT_ID,
            broker_host="localhost",
            pub_port=5555,
            sub_port=5556
        )
        
        # Inject the API key into the engine
        if not api_key:
            raise ValueError("API key must be provided to ClaudeClient.")
        self.engine = ClaudeApiEngine(api_key=api_key, model_name=model_name) # Pass model_name

    def process_incoming_message(self, message: Dict) -> None:
        """
        Overrides the base class method to provide Claude-specific logic
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
                response_text = self.engine.generate_response(message_text, message.get("metadata"), message.get("topic"))
                self.logger.info(f"Generated response: {response_text[:50]}...")
                
                response_content = {"message": response_text}
                
                # Send the response back to the original sender
                self.send_message(sender, "response", response_content, priority="HIGH")

            except Exception as e:
                self.logger.error(f"Failed to generate or send response: {e}", exc_info=True)
        
        elif message_type in ["response", "inform", "handshake"]:
             # For responses, informational messages, or handshakes, just log and do nothing.
             self.logger.info(f"Acknowledged '{message_type}' from {sender}.")
        
        else:
            # Handle unknown message types
            self.logger.warning(f"Received unknown message type '{message_type}' from {sender}. Ignoring.")

    def run(self):
        """
        The main run loop for the Claude client.
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
        except Exception as e:
            self.logger.fatal(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
        finally:
            self.cleanup()

    def cleanup(self):
        """Saves history and disconnects."""
        self.logger.info("Cleaning up and saving message history...")
        self.save_message_history()
        self.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Claude client.")
    parser.add_argument("--api-key", required=True, help="The Anthropic API key.")
    parser.add_argument("--model-name", type=str, default="claude-3-haiku-20240307", help="The Claude model to use.")
    args = parser.parse_args()

    claude_client = ClaudeClient(api_key=args.api_key, model_name=args.model_name)
    claude_client.run()