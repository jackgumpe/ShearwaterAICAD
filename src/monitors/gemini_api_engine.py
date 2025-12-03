import os
import google.generativeai as genai
import logging
from dotenv import load_dotenv
from pathlib import Path
from utilities.context_loader import ContextLoader
import hashlib
import argparse

class GeminiApiEngine:
    """
    An engine that connects to the live Google Gemini API to generate responses.
    """
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", num_messages: int = 10):
        if not api_key:
            raise ValueError("API key must be provided to GeminiApiEngine.")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.context_loader = ContextLoader()
        self.num_messages = num_messages
        self.logger = logging.getLogger(f"GeminiApiEngine-{model_name}")
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)
        self.cache = {}

    def generate_response(self, message_text: str, metadata: dict = None, topic: str = "general") -> str:
        """
        Generates a response by calling the Google Gemini API.
        """
        if not message_text:
            return "Received an empty message."

        try:
            context_summary = self.context_loader.get_context_summary(num_messages=self.num_messages)
            system_prompt = (
                f"{context_summary}\n\n"
                "You are 'gemini_cli', a helpful and brilliant AI assistant within the ShearwaterAICAD system. "
                "You are collaborating with another AI named 'claude_code'. "
                "Your responses should be concise, helpful, and reflect a collaborative spirit. "
                "Do not mention that you are an LLM or AI model."
            )

            full_prompt = f"{system_prompt}\n\nUser: {message_text}"
            
            prompt_hash = hashlib.md5(full_prompt.encode('utf-8')).hexdigest()

            if prompt_hash in self.cache:
                self.logger.info("Cache hit for this prompt. Returning cached response.")
                return self.cache[prompt_hash]

            self.logger.info(f"Generated Full Prompt (num_messages={self.num_messages}):\n---\n{full_prompt}\n---")
            response = self.model.generate_content(full_prompt)
            
            try:
                token_count = response.usage_metadata.prompt_token_count + response.usage_metadata.candidates_token_count
                self.logger.info(f"Token Usage: {token_count} (Prompt: {response.usage_metadata.prompt_token_count}, Response: {response.usage_metadata.candidates_token_count})")
            except Exception:
                pass

            response_text = response.text
            self.cache[prompt_hash] = response_text
            return response_text

        except Exception as e:
            self.logger.error(f"Error calling Google Gemini API: {e}", exc_info=True)
            return f"Error occurred while generating response: {e}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Gemini API engine directly for testing.")
    parser.add_argument("--api-key", required=True, help="The Google Gemini API key.")
    parser.add_argument("--num-messages", type=int, default=10, help="Number of recent messages to include in context.")
    parser.add_argument("--model-name", type=str, default="gemini-2.5-flash", help="The Gemini model to use.")
    args = parser.parse_args()

    engine = GeminiApiEngine(api_key=args.api_key, num_messages=args.num_messages, model_name=args.model_name)
    test_message = "Hello Gemini, this is a direct test of your API engine."
    response = engine.generate_response(test_message)
    print(f"Test Message: {test_message}")
    print(f"Gemini's Response: {response}")
    print("\nSending the same message again to test cache hit...")
    response_cached = engine.generate_response(test_message)
    print(f"Gemini's Cached Response: {response_cached}")