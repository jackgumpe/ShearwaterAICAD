import os
import anthropic
import logging
from dotenv import load_dotenv
from pathlib import Path
from utilities.context_loader import ContextLoader

class ClaudeApiEngine:
    """
    An engine that connects to the live Anthropic API to generate responses.
    """
    def __init__(self, api_key: str, model_name: str = "claude-3-haiku-20240307"):
        if not api_key:
            raise ValueError("API key must be provided to ClaudeApiEngine.")
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model_name
        self.context_loader = ContextLoader() # Instantiate ContextLoader
        self.logger = logging.getLogger(f"ClaudeApiEngine-{model_name}")
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def generate_response(self, message_text: str, metadata: dict = None, topic: str = "general") -> str:
        """
        Generates a response by calling the Anthropic messages API.
        """
        if not message_text:
            return "Received an empty message."

        try:
            context_summary = self.context_loader.get_context_summary()
            system_prompt = (
                f"{context_summary}\n\n"
                "You are 'claude_code', a helpful and brilliant AI assistant within the ShearwaterAICAD system. "
                "You are collaborating with another AI named 'gemini_cli'. "
                "Your responses should be concise, helpful, and reflect a collaborative spirit."
            )

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": message_text
                    }
                ]
            )

            response_text = ""
            if message.content and len(message.content) > 0:
                response_text = message.content[0].text
            
            # Log token usage
            if message.usage:
                self.logger.info(f"Token Usage: {message.usage.input_tokens + message.usage.output_tokens} (Input: {message.usage.input_tokens}, Output: {message.usage.output_tokens})")

            return response_text

        except Exception as e:
            self.logger.error(f"Error calling Anthropic API: {e}", exc_info=True)
            return f"Error occurred while generating response: {e}"

if __name__ == '__main__':
    # This block will now expect ANTHROPIC_API_KEY to be set in the shell environment
    # or by a parent process (like manage.py).
    engine = ClaudeApiEngine()
    test_message = "Hello Claude, this is a direct test of your API engine."
    response = engine.generate_response(test_message)
    print(f"Test Message: {test_message}")
    print(f"Claude's Response: {response}")