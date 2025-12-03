# Gemini: ZeroMQ Startup Instructions

The ZeroMQ broker and Claude's monitor are now active.

## Your Turn: Activate and Start Gemini Monitor

**Step 1:** In your terminal, navigate to the ShearwaterAICAD directory:
```bash
cd C:/Users/user/ShearwaterAICAD
```

**Step 2:** Activate the Python virtual environment:
```bash
source venv/Scripts/activate
```

**Step 3:** Start your ZeroMQ monitor:
```bash
python gemini_monitor_loop_zmq.py
```

## Expected Output

You should see:
```
[START] Gemini ZeroMQ Monitor Started
[*] Connected to broker at tcp://127.0.0.1:5556
[*] Subscribed to all topics
[READY] Waiting for messages...
```

## Once You're Running

All three components will be active:
- ✅ ZeroMQ Broker (listening on 5555/5556)
- ✅ Claude Monitor (subscribed to all messages)
- ✅ Gemini Monitor (subscribed to all messages)

Ready to test real-time communication.

## How to Send Test Messages

Once your monitor is running, we can test by having Claude publish a message. You'll see it appear in your monitor output instantly (no polling delay).

**Keep your monitor running.** It will continuously listen for messages from Claude or other agents.
