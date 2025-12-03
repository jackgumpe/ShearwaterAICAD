import zmq
import json
import time
from datetime import datetime

def main():
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect("tcp://localhost:5555")

    # Give the connection a moment to establish
    time.sleep(1)

    message = {
        'message_id': f"gemini_cli_test_{int(time.time()*1000)}",
        'timestamp': datetime.now().isoformat(),
        'sender_id': 'gemini_cli',
        "from": "gemini_cli",
        "to": "claude_code",
        "type": "request",
        "content": {
            "message": "Hello Claude, this is a test message from Gemini."
        },
        'metadata': {'sender_role': 'Test'}
    }

    topic = "claude_code".encode('utf-8')
    payload = json.dumps(message).encode('utf-8')

    pub_socket.send_multipart([topic, payload])
    print("Test message sent to claude_code.")

    pub_socket.close()
    context.term()

if __name__ == "__main__":
    main()