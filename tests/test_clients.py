import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from monitors.claude_client import ClaudeClient
from monitors.gemini_client import GeminiClient

class TestClaudeClient(unittest.TestCase):

    @patch('monitors.claude_client.LocalResponseEngine')
    def setUp(self, MockEngine):
        """Set up the test case, mocking dependencies."""
        # Mock the engine to provide a predictable response
        self.mock_engine_instance = MockEngine.return_value
        self.mock_engine_instance.generate_response.return_value = "This is a mock response."
        
        # Instantiate the client
        self.client = ClaudeClient()
        
        # Mock the low-level ZMQ socket to prevent actual network calls
        self.client.socket = MagicMock()
        self.client.is_connected = True

    @patch('monitors.claude_client.ClaudeClient.send_message')
    def test_process_incoming_message_generates_and_sends_response(self, mock_send_message):
        """
        Verify that processing a message triggers the response engine
        and calls send_message with the correct payload.
        """
        # 1. Arrange: Create a sample incoming message
        incoming_message = {
            "from": "gemini_cli",
            "content": {"message": "Hello Claude"},
            "metadata": {"chain_type": "test"}
        }

        # 2. Act: Call the method we want to test
        self.client.process_incoming_message(incoming_message)

        # 3. Assert
        # Verify the engine was asked to generate a response
        self.mock_engine_instance.generate_response.assert_called_once()

        # Verify that send_message was called
        mock_send_message.assert_called_once()

        # Check the arguments passed to send_message
        args, kwargs = mock_send_message.call_args
        
        recipient = args[0]
        message_type = args[1]
        content = args[2]

        self.assertEqual(recipient, "gemini_cli")
        self.assertEqual(message_type, "response")
        self.assertEqual(content["message"], "This is a mock response.")
        self.assertEqual(kwargs['priority'], "HIGH")

    def tearDown(self):
        """Clean up after the test."""
        self.client.cleanup()


class TestGeminiClient(unittest.TestCase):

    @patch('monitors.gemini_client.GeminiLocalEngine')
    def setUp(self, MockEngine):
        """Set up the test case, mocking dependencies."""
        # Mock the engine to provide a predictable response
        self.mock_engine_instance = MockEngine.return_value
        # The Gemini engine is expected to return a dictionary
        self.mock_engine_instance.generate_response.return_value = {
            "recipient_id": "claude_code",
            "type": "response",
            "content": {"message": "This is a Gemini mock response."}
        }
        
        # Instantiate the client
        self.client = GeminiClient()
        
        # Mock the low-level ZMQ socket
        self.client.socket = MagicMock()
        self.client.is_connected = True

    @patch('monitors.gemini_client.GeminiClient.send_message')
    def test_process_incoming_message_generates_and_sends_response(self, mock_send_message):
        """
        Verify that processing a message triggers the response engine
        and calls send_message with the correct payload from the engine.
        """
        # 1. Arrange: Create a sample incoming message
        incoming_message = {
            "from": "claude_code",
            "content": {"message": "Hello Gemini"},
        }

        # 2. Act: Call the method we want to test
        self.client.process_incoming_message(incoming_message)

        # 3. Assert
        # Verify the engine was asked to generate a response
        self.mock_engine_instance.generate_response.assert_called_once_with(incoming_message)

        # Verify that send_message was called
        mock_send_message.assert_called_once()

        # Check the arguments passed to send_message
        args, kwargs = mock_send_message.call_args
        
        recipient = args[0]
        message_type = args[1]
        content = args[2]

        self.assertEqual(recipient, "claude_code")
        self.assertEqual(message_type, "response")
        self.assertEqual(content["message"], "This is a Gemini mock response.")


    def tearDown(self):
        """Clean up after the test."""
        self.client.cleanup()


if __name__ == '__main__':
    unittest.main()
