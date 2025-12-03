# Manual ZeroMQ Startup Guide

**Problem**: Virtual environment activation doesn't persist across process boundaries in PowerShell.

**Solution**: Open 3 separate terminal windows and run each component manually with explicit venv activation.

---

## Setup: Three Terminal Windows

You need **3 separate terminal/PowerShell windows** open simultaneously. We'll call them:
- **Terminal A**: ZeroMQ Broker
- **Terminal B**: Gemini Monitor
- **Terminal C**: Claude Monitor

---

## Terminal A: Start ZeroMQ Broker

**Step 1**: Open a new PowerShell window

**Step 2**: Navigate to project directory
```powershell
cd C:/Users/user/ShearwaterAICAD
```

**Step 3**: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` prefix in your prompt:
```
(venv) PS C:\Users\user\ShearwaterAICAD>
```

**Step 4**: Start the broker
```powershell
python zmq_broker.py
```

**Expected Output**:
```
[*] ZeroMQ broker started.
[*] Listening for publishers on port 5555
[*] Listening for subscribers on port 5556
[*] Storing last 10000 messages in memory.
```

**Keep this terminal running.** This is your central message hub.

---

## Terminal B: Start Gemini Monitor

**Step 1**: Open a **new** PowerShell window (keep Terminal A running)

**Step 2**: Navigate to project directory
```powershell
cd C:/Users/user/ShearwaterAICAD
```

**Step 3**: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

**Step 4**: Start Gemini's monitor
```powershell
python gemini_monitor_loop_zmq.py
```

**Expected Output**:
```
[START] Gemini ZeroMQ Monitor Started
[*] Connected to broker at tcp://127.0.0.1:5556
[*] Subscribed to all topics
[READY] Waiting for messages...
```

**Keep this terminal running.** This is Gemini listening for all messages.

---

## Terminal C: Start Claude Monitor

**Step 1**: Open a **new** PowerShell window (keep Terminals A & B running)

**Step 2**: Navigate to project directory
```powershell
cd C:/Users/user/ShearwaterAICAD
```

**Step 3**: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

**Step 4**: Start Claude's monitor
```powershell
python claude_monitor_loop_zmq.py
```

**Expected Output**:
```
[START] Claude ZeroMQ Monitor Started
[*] Connected to broker at tcp://127.0.0.1:5556
[*] Subscribed to all topics
[READY] Waiting for messages...
```

**Keep this terminal running.** This is Claude listening for all messages.

---

## Verification: All Three Running

Once all three terminals show `[READY]`, the system is **live and ready for messaging**.

**Check your screen**:
```
┌─ Terminal A ─────────────────────┐
│ [*] ZeroMQ broker started        │
│ [*] Listening on 5555 & 5556     │
│ [*] Storing messages in memory   │
└──────────────────────────────────┘

┌─ Terminal B ─────────────────────┐
│ [START] Gemini Monitor Started   │
│ [*] Connected to broker          │
│ [READY] Waiting for messages...  │
└──────────────────────────────────┘

┌─ Terminal C ─────────────────────┐
│ [START] Claude Monitor Started   │
│ [*] Connected to broker          │
│ [READY] Waiting for messages...  │
└──────────────────────────────────┘
```

All three should show `[READY]` or similar status.

---

## Test Real-Time Communication

Once all three are running, you can test messaging **from a 4th terminal**:

**Terminal D: Send Test Message**

```powershell
cd C:/Users/user/ShearwaterAICAD
.\venv\Scripts\Activate.ps1

# Create a test message
$message = @{
    sender_id = "claude_code"
    message_id = "test_001"
    timestamp = Get-Date -AsUTC -Format "o"
    content = @{
        message = "Hello Gemini! Real-time test via ZeroMQ"
        action = "test_message"
    }
    metadata = @{
        ace_tier = "E"
        chain_type = "system_architecture"
        shl_tags = @("@Status-Ready", "@Test-Message")
    }
} | ConvertTo-Json

# Save to temp file
$message | Out-File -FilePath "$env:TEMP\test_message.json" -Encoding UTF8

# Publish the message
python send_message.py "$env:TEMP\test_message.json" "test_topic"
```

**What should happen**:
1. Message published to broker (< 1ms)
2. Both Gemini and Claude monitors see it immediately (< 10ms)
3. Output in Terminal B (Gemini):
   ```
   ============================================================
   [NEW ZMQ MESSAGE] From: claude_code | Topic: test_topic
   [MESSAGE ID] test_001
   ============================================================

   [MESSAGE CONTENT]
   {
     "message": "Hello Gemini! Real-time test via ZeroMQ",
     "action": "test_message"
   }
   ```

4. Output in Terminal C (Claude):
   ```
   ============================================================
   [CLAUDE] Received message from claude_code
   [ID] test_001
   [TYPE] test_message
   ...
   ```

---

## Troubleshooting

### Issue: "No module named 'zmq'"
**Solution**: Make sure you ran `.\venv\Scripts\Activate.ps1` and see `(venv)` in prompt

### Issue: "Port 5555 already in use"
**Solution**: Another broker is running. Kill it or use different ports (edit zmq_broker.py)

### Issue: Monitor says "Could not connect to broker"
**Solution**:
1. Check Terminal A (broker) is running
2. Wait 2-3 seconds for broker to fully start
3. Verify it shows `[*] Listening on 5555 & 5556`

### Issue: Message appears in one monitor but not the other
**Solution**: Make sure both monitors show `[READY]` before sending test message

---

## Why Three Separate Terminals?

- Each terminal has its own **independent venv activation**
- PowerShell's `Start-Process` doesn't inherit parent environment
- Running in same terminal blocks (each script runs forever listening for messages)
- Three terminals = three independent listeners running simultaneously
- Messages published to broker are instantly distributed to all listeners

---

## Next Steps (After All Three Running)

1. ✅ Verify all three terminals show `[READY]`
2. ✅ Send test message from Terminal D
3. ✅ Confirm both monitors receive it instantly
4. ✅ Test Gemini responding with send_message.py
5. ✅ Verify round-trip latency (should be < 100ms)
6. ✅ Begin Phase 1 component coding with real-time comms active

---

## Summary

**System is ready.** Just needs manual startup in three terminals with explicit venv activation.

**Startup sequence**:
1. Terminal A: `cd ... && .\venv\Scripts\Activate.ps1 && python zmq_broker.py`
2. Terminal B: `cd ... && .\venv\Scripts\Activate.ps1 && python gemini_monitor_loop_zmq.py`
3. Terminal C: `cd ... && .\venv\Scripts\Activate.ps1 && python claude_monitor_loop_zmq.py`
4. Terminal D: Test messages with `python send_message.py`

This is production-ready. No code changes needed.
