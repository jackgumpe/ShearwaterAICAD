"""
Llama Client - Third Agent in Multi-Agent Ensemble

Llama 3.1 70B Model
- Role: Reality-grounded generalist
- Strengths: Broad knowledge, grounded examples, assumption challenging
- Integration: Via Replicate or Together AI

This client follows the same AgentBaseClient pattern as Claude and Gemini.
"""

import os
import sys
import json
import argparse
import requests
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.clients.agent_base_client import AgentBaseClient


class LlamaClient(AgentBaseClient):
    """
    Llama 3.1 70B Chat Model Client

    Llama is the reality-grounded generalist in the multi-agent ensemble.
    It brings:
    - Broad general knowledge
    - Practical, grounded thinking
    - Alternative perspectives
    - Common-sense reality checks
    """

    def __init__(self, api_key, model_name="meta-llama/llama-2-70b-chat"):
        """Initialize Llama client"""
        super().__init__(agent_name="llama_agent")

        self.api_key = api_key
        self.model_name = model_name
        self.provider = "replicate"  # Can be "replicate", "together", or "self-hosted"

        # System prompt for Llama's role in multi-agent ensemble
        self.system_prompt = """You are Llama, the reality-grounded generalist agent in a multi-agent AI ensemble.

Your Strengths:
- Broad, practical knowledge across many domains
- Grounding in real-world examples and constraints
- Ability to challenge overly theoretical approaches
- Alternative perspectives that others might miss
- Common-sense reasoning

Your Role in Collaboration:
When interacting with Claude (detail-oriented analyst), Gemini (creative synthesizer), and other agents:

1. REALITY CHECK: Ask "Is this grounded in reality?" and "Can this actually work?"
2. GROUNDING: Provide real-world examples, constraints, and practical limitations
3. ALTERNATIVE VIEWS: Suggest different approaches or ways to look at problems
4. ASSUMPTION CHALLENGE: Question unspoken assumptions and "obvious" truths
5. PRACTICAL WISDOM: Balance between theoretical correctness and real-world feasibility

Specific Techniques:
- Ask: "What happens in practice?" "What could go wrong?"
- Say: "From my general knowledge..." "In real-world scenarios..."
- Challenge: "Have we considered..." "What if the assumption is wrong?"
- Ground: "For example..." "In practice, this means..."

In Multi-Agent Discussions:
- Value the analysis of Claude, synthesis of Gemini, and others
- Add your unique perspective based on broad knowledge
- Don't just agree - contribute something different
- Ask clarifying questions about feasibility and grounding
- Help identify what's missing or what could be overlooked

Conversation Style:
- Clear, accessible explanations
- Mix theoretical understanding with practical examples
- Honest about limitations and uncertainties
- Collaborative and respectful to other agents
- Focused on creating better solutions together"""

        self.message_history = []
        self.logger.info(f"Llama client initialized (Provider: {self.provider})")

    def _call_llama_api(self, messages, temperature=0.7, max_tokens=2000):
        """
        Call Llama API via Replicate or Together AI

        Supports multiple providers for flexibility.
        """

        if self.provider == "replicate":
            return self._call_replicate(messages, temperature, max_tokens)
        elif self.provider == "together":
            return self._call_together(messages, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _call_replicate(self, messages, temperature, max_tokens):
        """Call Llama via Replicate API"""

        try:
            import replicate

            # Format messages for Llama
            prompt = self._format_messages_for_llama(messages)

            output = replicate.run(
                self.model_name,
                input={
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": 0.9,
                    "top_k": 50,
                }
            )

            # Replicate returns list of strings
            response = "".join(output) if isinstance(output, list) else output

            return {
                "content": response,
                "tokens_used": len(response.split()),  # Rough estimate
                "provider": "replicate"
            }

        except ImportError:
            self.logger.error("Replicate library not installed. Install with: pip install replicate")
            raise
        except Exception as e:
            self.logger.error(f"Replicate API error: {e}")
            raise

    def _call_together(self, messages, temperature, max_tokens):
        """Call Llama via Together AI API"""

        try:
            import together

            together.api_key = self.api_key

            # Format messages for Llama
            prompt = self._format_messages_for_llama(messages)

            output = together.Complete.create(
                prompt=prompt,
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.1,
                stop=["<|end|>", "<|eot_id|>"]
            )

            response = output["output"]["choices"][0]["text"]

            return {
                "content": response.strip(),
                "tokens_used": len(response.split()),
                "provider": "together"
            }

        except ImportError:
            self.logger.error("Together library not installed. Install with: pip install together")
            raise
        except Exception as e:
            self.logger.error(f"Together API error: {e}")
            raise

    def _format_messages_for_llama(self, messages):
        """Format messages in Llama chat format"""

        prompt = ""

        # Add system prompt
        prompt += f"[SYSTEM]\n{self.system_prompt}\n\n"

        # Add conversation history
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                prompt += f"[USER]\n{content}\n\n"
            elif role == "assistant":
                prompt += f"[ASSISTANT]\n{content}\n\n"
            else:
                prompt += f"[{role.upper()}]\n{content}\n\n"

        # Add prompt for next response
        prompt += "[ASSISTANT]\n"

        return prompt

    def process_incoming_message(self, message):
        """
        Process incoming message and generate response

        Called by message broker when a message arrives for this agent.
        """

        try:
            sender = message.get("from", "unknown")
            msg_type = message.get("type", "unknown")
            content = message.get("content", {}).get("message", "")

            self.logger.info(f"Received message from {sender} (type: {msg_type})")
            self.logger.debug(f"Content: {content[:100]}...")

            # Add to conversation history
            self.message_history.append({
                "role": "user",
                "content": f"{sender}: {content}"
            })

            # Generate response using Llama
            response = self._generate_response(content, sender, msg_type)

            # Add response to history
            self.message_history.append({
                "role": "assistant",
                "content": response
            })

            # Send response back
            self.send_message(
                from_agent="llama_agent",
                to_agent=sender,
                message_type="response",
                content=response
            )

            return True

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _generate_response(self, content, from_agent, msg_type):
        """
        Generate Llama response to message

        Uses the system prompt to ensure Llama acts as a reality-grounding
        generalist who brings alternative perspectives.
        """

        # Temperature varies based on message type
        if msg_type == "request":
            temperature = 0.8  # More creative for open questions
        elif msg_type == "response":
            temperature = 0.7  # Balanced for follow-up
        else:
            temperature = 0.6  # More focused for decisions

        # Call Llama API
        api_response = self._call_llama_api(
            messages=self.message_history,
            temperature=temperature,
            max_tokens=2000
        )

        response_text = api_response["content"]

        # Format response
        formatted_response = f"""[Llama's Analysis]

From the perspective of grounded, practical thinking:

{response_text}

---
Role: Reality-grounded generalist
Provider: {api_response.get('provider', 'unknown')}
"""

        return formatted_response

    def run_loop(self):
        """
        Main event loop for Llama agent

        Listens for messages on SUB socket and processes them.
        """

        self.logger.info("Llama client starting event loop...")

        try:
            while True:
                # Check for incoming messages
                try:
                    socket, message = self.receive_message(timeout=1000)

                    if message:
                        self.process_incoming_message(message)

                except:
                    # Timeout or no message, continue
                    pass

                # Periodic heartbeat (optional)
                time.sleep(0.1)

        except KeyboardInterrupt:
            self.logger.info("Llama client shutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up Llama client...")
        super().cleanup()


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description="Llama Agent Client")
    parser.add_argument("--api-key", type=str, required=True, help="API key for Replicate or Together AI")
    parser.add_argument("--model-name", type=str, default="meta-llama/llama-2-70b-chat", help="Llama model name")
    parser.add_argument("--provider", type=str, default="replicate", choices=["replicate", "together"], help="API provider")
    parser.add_argument("--broker-host", type=str, default="localhost", help="Message broker host")
    parser.add_argument("--pub-port", type=int, default=5555, help="Broker PUB port")
    parser.add_argument("--sub-port", type=int, default=5556, help="Broker SUB port")

    args = parser.parse_args()

    # Create and run client
    client = LlamaClient(api_key=args.api_key, model_name=args.model_name)
    client.provider = args.provider
    client.broker_host = args.broker_host
    client.broker_pub_port = args.pub_port
    client.broker_sub_port = args.sub_port

    client.run_loop()


if __name__ == "__main__":
    main()
