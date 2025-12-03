# Quick Start: Option 3 - Full Parallel Execution

## TL;DR - Just Run These Commands

### Step 1: Open Terminal A
```powershell
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python zmq_broker_enhanced.py
```
Wait for: `[READY] Listening on ports 5555/5556`

### Step 2: Open Terminal B (wait 2 sec after A is ready)
```powershell
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python gemini_monitor_loop_zmq.py
```
Wait for: `[READY] Waiting for messages...`

### Step 3: Open Terminal C (wait 2 sec after B is ready)
```powershell
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python claude_monitor_loop_zmq.py
```
Wait for: `[READY] Waiting for messages...`

### Step 4: Test (Terminal D)
```powershell
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1

$msg = @{
    sender_id = "claude_code"
    message_id = "test_001"
    timestamp = Get-Date -AsUTC -Format "o"
    content = @{ message = "Test message" }
    metadata = @{ ace_tier = "E"; chain_type = "system_architecture" }
} | ConvertTo-Json

$msg | Out-File "test.json"
python send_message.py test.json general
```

✅ If all three terminals show the message in 1 second = **HANDSHAKE LIVE**

---

## Step 5: Start Block Consolidation (Terminal D or new)
```powershell
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python block_consolidation_bot_v1.py
```

Expected result: Converts 2,367 messages → ~300-400 blocks in ~5 minutes

---

## Step 6: Keep Old System Running (Terminal E - optional)
```powershell
cd C:/Users/user/ShearwaterAICAD
.\\venv\\Scripts\\Activate.ps1
python claude_monitor_loop.py
```

This gives you backup while testing new ZeroMQ system.

---

## What You Now Have

✅ **Real-time communication**: <10ms latency between Gemini and Claude
✅ **Conversation blocks**: 2,367 messages consolidated into 300-400 blocks
✅ **Backup inbox**: Old file-based system still working
✅ **Research complete**: Everything needed for next phases documented

---

## Next Steps After Launch

1. **Verify all three ZeroMQ terminals show [READY]**
2. **Test message delivery** - should be <50ms
3. **Run block_consolidation_bot_v1.py** - takes ~5 minutes
4. **Review blocks_index_v1.jsonl** - check output format
5. **Start Phase 1 component design** - while you have working system
6. **Discuss blocks with Gemini** - via ZeroMQ handshake

---

## Files Created for Option 3

- `LAUNCH_INSTRUCTIONS_OPTION3.md` - Detailed launch guide
- `block_consolidation_bot_v1.py` - Basic segmentation bot
- `QUICK_START_OPTION3.md` - This file
- `RESEARCH_FINDINGS_DETAILED.md` - Full research (already done)

---

## Troubleshooting

**Ports already in use?**
```powershell
# Kill existing process
Get-Process python | Where-Object {$_.Name -like "*zmq*"} | Stop-Process -Force
```

**Models not downloaded yet?**
- First run of all-MiniLM-L6-v2 takes a minute
- Subsequent runs use cached model

**Old inbox still showing errors?**
- That's fine, keep running it as backup
- ZeroMQ terminals take priority

---

## Timeline

- **T+5 min**: All three ZeroMQ terminals [READY]
- **T+10 min**: Test message verified, handshake confirmed
- **T+15 min**: block_consolidation_bot_v1.py running
- **T+20 min**: blocks_index_v1.jsonl complete (~300-400 blocks)
- **T+20-60 min**: Start Phase 1 component development

---

🚀 **Ready? Run the 3 terminal commands above.**
