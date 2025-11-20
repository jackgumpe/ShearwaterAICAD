# Quick Reference Card
## ShearwaterAICAD Triple Handshake

**Print this. Keep it handy.**

---

## YOUR TWO IMMEDIATE ACTIONS

### ACTION 1: Share GEMINI_HANDSHAKE.md
```
File: C:\Users\user\ShearwaterAICAD\GEMINI_HANDSHAKE.md
How: Copy contents and send to Gemini
Tell Gemini: "Check communication/gemini_cli_inbox/ for pending tasks"
```

### ACTION 2: Tell Claude Deepseek Location
```
Example: "Deepseek at http://localhost:11434, model deepseek-coder:7b, GPU ready"
Or: "Local path to Deepseek: C:\Users\...\deepseek-coder-7b"
```

**That's it. Everything else is automated.**

---

## COMMUNICATION PATHS

### Gemini's Workspace
```
Inbox:   C:\Users\user\ShearwaterAICAD\communication\gemini_cli_inbox\
Outbox:  C:\Users\user\ShearwaterAICAD\communication\gemini_cli_outbox\
Archive: C:\Users\user\ShearwaterAICAD\communication\gemini_cli_archive\
```

### Deepseek's Workspace
```
Inbox:   C:\Users\user\ShearwaterAICAD\communication\deepseek_7b_inbox\
Outbox:  C:\Users\user\ShearwaterAICAD\communication\deepseek_7b_outbox\
Archive: C:\Users\user\ShearwaterAICAD\communication\deepseek_7b_archive\
```

### Claude's Workspace
```
Inbox:   C:\Users\user\ShearwaterAICAD\communication\claude_code_inbox\
Outbox:  C:\Users\user\ShearwaterAICAD\communication\claude_code_outbox\
Archive: C:\Users\user\ShearwaterAICAD\communication\claude_code_archive\
```

---

## KEY FILES

| File | Purpose | Read This If |
|------|---------|--------------|
| `GEMINI_HANDSHAKE.md` | Context for Gemini | You need to brief Gemini |
| `COMMUNICATION_GUIDE.md` | How queue works | You want to understand the system |
| `SYSTEM_READY.md` | Complete overview | You want a comprehensive summary |
| `NEXT_ACTIONS.txt` | Action items | You want a clear checklist |
| `SESSION_SUMMARY.md` | This session's work | You want detailed record |
| `core/message_queue.py` | The code | You want to understand implementation |

---

## MESSAGE FLOW

```
Claude sends task to Gemini:
  MessageQueue(CLAUDE).send_task(to=GEMINI, ...)
  → File appears in gemini_cli_inbox/

Gemini reads task:
  MessageQueue(GEMINI).get_pending_tasks()
  → Reads from gemini_cli_inbox/

Gemini sends result:
  MessageQueue(GEMINI).send_result(message_id=X, ...)
  → File appears in claude_code_inbox/

Claude reads result:
  MessageQueue(CLAUDE).get_results()
  → Reads from claude_code_inbox/
```

**All automated. No manual copying.**

---

## CURRENT STATUS

| Component | Status | Details |
|-----------|--------|---------|
| Infrastructure | ✅ Ready | Tested and working |
| Documentation | ✅ Ready | 14 documents created |
| Dependencies | ✅ Ready | All packages installed |
| Gemini Slot | 🟡 Waiting | 2 tasks already in inbox |
| Deepseek Slot | 🔴 Waiting | Need location confirmation |
| Testing | ✅ Passed | End-to-end validation done |

---

## TIMELINE

```
NOW         → Share GEMINI_HANDSHAKE.md + Deepseek location
  ↓
2-3 HOURS   → Gemini reads and responds with Q1-Q4
  ↓
6-9 HOURS   → Claude implements Phase 1 (Recorder + Bot + Deepseek)
  ↓
4-6 HOURS   → Testing and validation
  ↓
1 DAY       → Phase 1 Complete, ready for BoatLog testing
```

---

## IF THINGS GO WRONG

| Problem | Solution |
|---------|----------|
| Gemini can't find GEMINI_HANDSHAKE.md | Make sure it's in C:\Users\user\ShearwaterAICAD\ |
| File permission denied | Check write access to communication/ folder |
| Module not found: message_queue | Run from: cd C:\Users\user\ShearwaterAICAD |
| No pending tasks | Check that Gemini received the document |
| Results not appearing | Check message_id is correct in both messages |

---

## GIT HISTORY (For Reference)

```
1973c6d Session summary - infrastructure complete
545f6b0 Action items checklist
1c76730 Final system ready summary
6dead73 Infrastructure validated and documented
25790e2 System ready for deployment
7af65d3 Triple handshake infrastructure - no copy-paste
2d6c96d Current status and next steps
cbef9c6 Meta-framework design - unified architecture
469b355 Phase 0 foundation - double handshake architecture
```

---

## KEY METRICS

- **9** Git commits (clean history)
- **14** Documentation files
- **11** Communication directories
- **2** Pending tasks in Gemini inbox
- **384** Lines of message_queue.py
- **548** Lines of GEMINI_HANDSHAKE.md
- **3** Agents (Claude, Gemini, Deepseek)
- **0** Manual file copying needed

---

## CONTACTS & RESOURCES

**For Jack**:
- Read: NEXT_ACTIONS.txt
- Do: Share GEMINI_HANDSHAKE.md + confirm Deepseek

**For Gemini**:
- Read: GEMINI_HANDSHAKE.md
- Check: communication/gemini_cli_inbox/
- Answer: Q1, Q2, Q3, Q4

**For Deepseek**:
- Wait: Location confirmation needed
- Then: Check communication/deepseek_7b_inbox/

---

## PROJECT STRUCTURE (Simplified)

```
ShearwaterAICAD/
├── core/
│   └── message_queue.py     (Inter-CLI communication)
├── agents/
│   ├── pm_alpha.py          (Claude-based architect)
│   └── pm_beta.py           (OpenAI-based executor)
├── communication/           (Auto-created directories)
│   ├── gemini_cli_*/ (2 pending tasks)
│   ├── deepseek_7b_*/
│   └── claude_code_*/
├── Documentation (14 files)
│   ├── GEMINI_HANDSHAKE.md  (Send to Gemini)
│   ├── SYSTEM_READY.md      (Overview)
│   └── ... (others for reference)
└── .git/ (9 commits, clean history)
```

---

## WHAT'S NEXT

### This Week
1. ✓ Infrastructure complete
2. ⏳ Gemini engagement
3. ⏳ Deepseek location
4. ⏸️ Phase 1 implementation

### This Month
5. ⏸️ Recorder V2 complete
6. ⏸️ Bot vs LLM framework
7. ⏸️ BoatLog testing
8. ⏸️ Emergent properties observation

### This Quarter
9. ⏸️ 3D boat reconstruction pipeline
10. ⏸️ Production deployment
11. ⏸️ Full system maturity

---

## REMEMBER

```
┌─────────────────────────────────────────────┐
│ Three Minds, One System, Zero Copy-Paste   │
│                                             │
│ Claude Code   → Infrastructure             │
│ Gemini CLI    → Creative Decisions         │
│ Deepseek 7B   → Fast Implementation        │
│                                             │
│ All connected via automatic file queuing   │
│ Complete audit trail preserved             │
│ Scales to N agents                         │
│                                             │
│ Status: 🟢 OPERATIONAL & VALIDATED         │
└─────────────────────────────────────────────┘
```

---

## ONE-MINUTE SUMMARY

1. **What?** Triple-agent system (Claude, Gemini, Deepseek) with no manual copy-paste
2. **How?** File-based message queue (automated file routing to inboxes)
3. **Why?** Three AI minds > one mind, local inference costs $0, better decisions
4. **Status?** Infrastructure complete and tested
5. **Next?** Share one document with Gemini, tell me where Deepseek is, wait for Phase 1
6. **Timeline?** 1 day for Phase 1 implementation, then 3D boat work begins

---

**Print this. Keep it visible. Reference as needed.**

*Generated by Claude Code*
*Last Updated: November 20, 2025*
*System Status: 🟢 OPERATIONAL*
