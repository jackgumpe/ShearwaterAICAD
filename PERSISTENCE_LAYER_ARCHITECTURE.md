# Independent Persistence Layer Architecture

**Status:** BLUEPRINT
**Priority:** CRITICAL - System redesign for production robustness
**Goal:** Decouple persistence from broker, create autonomous persistence service

---

## Current Problem (What We're Fixing)

```
CURRENT (COUPLED):
┌─────────────────────────────────────┐
│         ZeroMQ Broker               │
│  - Message forwarding (XPUB/XSUB)  │
│  - Recording (COUPLED)              │ ◄─── PROBLEM: Single point of failure
│  - Persistence (COUPLED)            │
│  - Metadata enrichment (COUPLED)    │
└─────────────────────────────────────┘
         │
         └──► conversation_logs/current_session.jsonl

RISK: Change broker = risk persistence
RISK: Lose broker = lose checkpoint system
```

---

## Proposed Solution (Decoupled)

```
PROPOSED (DECOUPLED):

┌──────────────────────────────────┐
│   ZeroMQ Broker (PURE)          │
│   - Only message forwarding      │
│   - XPUB/XSUB proxy             │
│   NO persistence code            │
│   NO recording code              │
│   NO metadata code               │
└──────────────────────────────────┘
         │
         │ [messages flow through]
         ▼
┌──────────────────────────────────────────────────┐
│   INDEPENDENT PERSISTENCE LAYER                 │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │  Persistence Service (persistence_daemon.py) │ │
│  │  - Listens to message stream               │ │
│  │  - Records all messages                    │ │
│  │  - Applies metadata enrichment             │ │
│  │  - Manages checkpoints                     │ │
│  │  - Handles recovery                        │ │
│  └────────────────────────────────────────────┘ │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │  Storage Layer (database + JSONL)          │ │
│  │  - conversation_logs/ (append-only)        │ │
│  │  - checkpoints/ (snapshots)                │ │
│  │  - metadata_index/ (searchable)            │ │
│  │  - recovery/ (crash recovery files)        │ │
│  └────────────────────────────────────────────┘ │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │  CLI Manager (persistence_cli.py)          │ │
│  │  - Interactive checkpoint selector         │ │
│  │  - Recovery tools                          │ │
│  │  - Metadata browser                        │ │
│  │  - System diagnostics                      │ │
│  └────────────────────────────────────────────┘ │
│                                                   │
│  ┌────────────────────────────────────────────┐ │
│  │  Auto-Launcher (persistence_launcher.py)  │ │
│  │  - Detects agent connection                │ │
│  │  - Auto-starts on project load             │ │
│  │  - Shows checkpoint menu                   │ │
│  │  - Handles graceful shutdown               │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
         │
         ├──► conversation_logs/current_session.jsonl
         ├──► checkpoints/checkpoint_*.json
         ├──► metadata_index/index.db
         └──► recovery/crash_recovery.jsonl

BENEFITS:
✅ Broker can change without affecting persistence
✅ Persistence can evolve independently
✅ Autonomous operation - starts when needed
✅ Easy to test/debug/replace each component
✅ Single responsibility principle
```

---

## Directory Structure

```
project_root/
├── src/
│   ├── brokers/
│   │   └── zmq_broker_enhanced.py (UNCHANGED - pure message forwarding)
│   │
│   ├── persistence/  (NEW LAYER)
│   │   ├── __init__.py
│   │   ├── persistence_daemon.py
│   │   │   ├── EnhancedConversationRecorder (moved here)
│   │   │   ├── MetadataEnricher
│   │   │   ├── CheckpointManager
│   │   │   └── CrashRecoveryManager
│   │   │
│   │   ├── persistence_cli.py
│   │   │   ├── CheckpointSelector (interactive menu)
│   │   │   ├── ConversationBrowser
│   │   │   ├── MetadataAnalyzer
│   │   │   └── SystemDiagnostics
│   │   │
│   │   ├── persistence_launcher.py
│   │   │   ├── AgentConnectionDetector
│   │   │   ├── AutoStartManager
│   │   │   └── GracefulShutdown
│   │   │
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── message_store.py
│   │   │   ├── checkpoint_store.py
│   │   │   └── metadata_index.py
│   │   │
│   │   └── recovery/
│   │       ├── __init__.py
│   │       ├── crash_recovery.py
│   │       └── checkpoint_recovery.py
│   │
│   └── monitors/
│       ├── claude_client.py
│       └── gemini_client.py
│
├── conversation_logs/
│   ├── current_session.jsonl
│   ├── archive/
│   ├── checkpoints/
│   │   ├── checkpoint_20251130_100000.json
│   │   ├── checkpoint_20251130_120000.json
│   │   └── ...
│   ├── metadata_index/
│   │   └── index.db (SQLite for fast querying)
│   └── recovery/
│       └── crash_recovery.jsonl
│
├── manage.py (UNCHANGED)
├── persistence.py (NEW - entry point for persistence system)
└── docs/
    └── PERSISTENCE_LAYER_ARCHITECTURE.md
```

---

## Core Components

### 1. Persistence Daemon (`src/persistence/persistence_daemon.py`)

**Purpose:** Background process that records all messages independently

```python
class PersistenceService:
    def __init__(self):
        self.broker_socket = self._connect_to_broker()
        self.recorder = EnhancedConversationRecorder()
        self.checkpoint_manager = CheckpointManager()
        self.recovery_manager = CrashRecoveryManager()

    def start(self):
        """Run persistence service"""
        while True:
            message = self.broker_socket.recv_multipart()
            event = self.recorder.process_and_enrich(message)
            self.recorder.persist(event)
            self.checkpoint_manager.check_for_checkpoint()
            self.recovery_manager.update_recovery_file()

    def graceful_shutdown(self):
        """Save state before closing"""
        self.checkpoint_manager.create_emergency_checkpoint()
        self.recovery_manager.finalize()
```

**Responsibilities:**
- ✅ Listen to broker message stream (doesn't modify it)
- ✅ Record every message to JSONL
- ✅ Apply metadata enrichment
- ✅ Manage checkpoints
- ✅ Handle crash recovery
- ✅ Update search index

**No dependencies on broker internals** - just listens to message stream

---

### 2. Persistence CLI (`src/persistence/persistence_cli.py`)

**Purpose:** Interactive CLI for checkpoint management and recovery

```python
class PersistenceCLI:
    def __init__(self):
        self.checkpoint_store = CheckpointStore()
        self.conversation_browser = ConversationBrowser()
        self.metadata_analyzer = MetadataAnalyzer()

    def show_checkpoint_menu(self):
        """Interactive menu for loading checkpoints"""
        print("=" * 60)
        print("  SHEARWATER CONVERSATION RECOVERY")
        print("=" * 60)

        checkpoints = self.checkpoint_store.list_all()

        if not checkpoints:
            print("\n✓ No previous checkpoints found")
            print("  System ready for new session")
            return

        print(f"\n✓ Found {len(checkpoints)} checkpoint(s)\n")

        for i, cp in enumerate(checkpoints, 1):
            size = cp['size_mb']
            time = cp['timestamp']
            msgs = cp['message_count']
            print(f"  [{i}] {time} | {msgs} msgs | {size}MB")

        print("\n  [L]oad checkpoint")
        print("  [N]ew session")
        print("  [V]iew recent messages")
        print("  [S]earch conversations")
        print("  [D]iagnostics")
        print("  [Q]uit\n")

        choice = input("  Choice: ").strip().upper()

        if choice == 'L':
            self._load_checkpoint_interactive()
        elif choice == 'V':
            self._view_recent()
        elif choice == 'S':
            self._search()
        # ... etc

    def _load_checkpoint_interactive(self):
        """Let user select and load a checkpoint"""
        checkpoints = self.checkpoint_store.list_all()
        idx = int(input("  Checkpoint number: ")) - 1
        checkpoint = checkpoints[idx]

        print(f"\n✓ Loading checkpoint from {checkpoint['timestamp']}...")
        self.checkpoint_store.load(checkpoint['id'])
        print("✓ Checkpoint restored")

    def _view_recent(self):
        """Show recent conversation snippets"""
        recent = self.conversation_browser.get_recent_messages(10)
        for msg in recent:
            print(f"  {msg['timestamp']}: {msg['sender']} > {msg['preview']}")

    def _search(self):
        """Search conversations by keyword"""
        query = input("  Search term: ")
        results = self.metadata_analyzer.search(query)
        print(f"✓ Found {len(results)} messages")
        for r in results[:5]:
            print(f"  - {r['timestamp']}: {r['preview']}")
```

**Interaction Flow:**
```
Agent connects to project
         │
         ▼
persistence_launcher detects
         │
         ▼
┌─────────────────────────────────┐
│   CHECKPOINT SELECTION MENU     │
├─────────────────────────────────┤
│                                 │
│  SHEARWATER RECOVERY            │
│                                 │
│  [1] 2025-11-30 10:00 | 2349 msgs
│  [2] 2025-11-29 15:30 | 5612 msgs
│  [3] 2025-11-28 08:15 | 8901 msgs
│                                 │
│  [L]oad  [N]ew  [V]iew [S]earch │
│  [D]iags [Q]uit                 │
│                                 │
│  Choice: _                       │
└─────────────────────────────────┘
         │
    User selects
         │
         ▼
  Checkpoint loads
  or New session starts
```

---

### 3. Persistence Launcher (`src/persistence/persistence_launcher.py`)

**Purpose:** Auto-starts persistence when agent connects, shows menu

```python
class PersistenceLauncher:
    def __init__(self):
        self.daemon_process = None
        self.cli = PersistenceCLI()

    def on_agent_connected(self):
        """Called when Claude/Gemini CLI connects to project"""
        print("\n[PERSISTENCE] Agent detected")

        # 1. Start persistence daemon in background
        self.daemon_process = self._start_daemon()
        print("[PERSISTENCE] Daemon started (PID: {})".format(self.daemon_process.pid))

        # 2. Show checkpoint menu
        self.cli.show_checkpoint_menu()

        # 3. Continue with agent operation
        return True

    def _start_daemon(self):
        """Start persistence service as subprocess"""
        import subprocess
        process = subprocess.Popen(
            ["python", "-m", "persistence.persistence_daemon"],
            cwd="src"
        )
        return process

    def on_agent_disconnected(self):
        """Called when agent closes"""
        print("\n[PERSISTENCE] Agent disconnected")
        self._save_session_checkpoint()
        self._stop_daemon()

    def _save_session_checkpoint(self):
        """Auto-save checkpoint when agent closes"""
        cp = self.cli.checkpoint_store.create_checkpoint(
            label=f"auto_save_{datetime.now().isoformat()}"
        )
        print(f"[PERSISTENCE] Session saved: {cp['id']}")

    def _stop_daemon(self):
        """Gracefully stop persistence daemon"""
        if self.daemon_process:
            self.daemon_process.terminate()
            self.daemon_process.wait(timeout=5)
```

---

### 4. Storage Layer (`src/persistence/storage/`)

**Responsibilities:**
- Append-only JSONL logging
- SQLite index for fast searching
- Atomic checkpoint creation
- Recovery file management

```python
class MessageStore:
    def append_message(self, event: ConversationEvent) -> None:
        """Atomically append message to log"""
        with atomic_write_lock:
            with open(CURRENT_LOG_FILE, 'a') as f:
                f.write(json.dumps(asdict(event)) + '\n')
                f.flush()
                os.fsync(f.fileno())

class CheckpointStore:
    def create_checkpoint(self, label: str) -> CheckpointRef:
        """Create immutable snapshot of current state"""
        # Copy current_session.jsonl to checkpoints/
        # Create checkpoint metadata
        # Update index

class MetadataIndex:
    def search(self, query: str) -> List[MessageRef]:
        """Fast search using SQLite index"""
        # Query index database
        # Return matching message references
```

---

## Startup Sequence

### When Claude Code connects:

```
1. detect_agent_connection()
        │
        ▼
2. PersistenceLauncher.on_agent_connected()
        │
        ├──► Start persistence daemon (background)
        │    └──► persistence_daemon.py starts
        │        └──► Connects to broker
        │        └──► Begins recording
        │
        └──► Show CLI Menu
             └──► CheckpointSelector.show_menu()
                 └──► User chooses:
                     ├─ Load old checkpoint
                     ├─ Start new session
                     ├─ View recent messages
                     └─ Search conversations
```

### When agent disconnects:

```
claude_client.disconnect()
        │
        ▼
PersistenceLauncher.on_agent_disconnected()
        │
        ├──► Create emergency checkpoint
        │    └──► Auto-save session state
        │
        └──► Graceful daemon shutdown
             └──► Save recovery file
             └──► Close all handles
             └──► Exit process
```

---

## Independence Benefits

### ✅ Broker Can Change
- Remove broker code entirely? No problem.
- Switch to different messaging system? Persistence doesn't care.
- Rewrite broker from scratch? Persistence keeps working.

### ✅ Persistence Can Evolve
- Add new metadata types? Just modify MetadataEnricher.
- Switch storage backend? Just reimplement StorageLayer.
- Add compression? Add to CheckpointManager.
- Add encryption? Add security layer.

### ✅ Autonomous Operation
- Starts automatically when agent connects
- Doesn't require manual startup
- Gracefully handles crashes
- Auto-recovers on restart

### ✅ Easy Testing
- Test persistence independently from broker
- Mock the message stream
- Inject test messages
- Verify recording without full system

### ✅ Production Robustness
- Single point of failure eliminated
- Persistence survives broker crashes
- Broker survives persistence crashes
- Each layer can be restarted independently

---

## Phase 1 Implementation (Next 4-6 hours)

1. **Create persistence package structure**
   - New directories in `src/persistence/`
   - Move recording logic out of broker
   - Create storage layer abstraction

2. **Build persistence daemon**
   - Listen to broker (don't modify)
   - Record messages independently
   - Handle checkpoints

3. **Build CLI menu system**
   - Interactive checkpoint selector
   - Conversation viewer
   - Search capability

4. **Build launcher/auto-start**
   - Detect agent connection
   - Start daemon in background
   - Show menu, then continue

5. **Integration testing**
   - Start agent → see menu
   - Load checkpoint → conversation restored
   - Create checkpoint → verify saved
   - Crash daemon → verify recovery

---

## Success Criteria

After implementation:

✅ Persistence runs independently from broker
✅ Persistence daemon auto-starts when agent connects
✅ Checkpoint menu shows on agent startup
✅ User can load previous conversations
✅ System recovers from daemon crashes
✅ Broker can be updated without affecting persistence
✅ Persistence can be updated without affecting broker
✅ Each component can be tested in isolation
✅ No coupling between broker and persistence code

---

## Timeline

- **Daemon service:** 1.5 hours
- **CLI menu:** 1 hour
- **Storage layer:** 1 hour
- **Launcher/auto-start:** 0.5 hours
- **Integration & testing:** 1 hour

**Total: ~5 hours for production-ready system**

---

## Deployment

```bash
# Start persistence system explicitly
python -m persistence.persistence_launcher

# Or let it auto-start (when integrated with agents)
python manage.py start  # Detects agents, starts persistence

# View/manage checkpoints
python -m persistence.persistence_cli
```

---

## Conclusion

This architecture:
- Decouples persistence from broker
- Makes persistence autonomous
- Adds elegant CLI for checkpoint recovery
- Enables independent evolution of components
- Provides enterprise-grade robustness
- Still preserves all current functionality

The persistence layer becomes a true independent system - not an afterthought bolted onto the broker.
