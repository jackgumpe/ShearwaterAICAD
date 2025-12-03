# Visual Architecture Comparison
**Date**: 2025-11-28

## Current Synaptic Mesh (ZeroMQ ROUTER-DEALER)

```
                    ┌────────────────────┐
                    │   Root Router      │
                    │   (ZMQ ROUTER)     │
                    │   Port: 5550       │
                    └──────────┬─────────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
    ┌──────────▼─────────┐         ┌──────────▼─────────┐
    │  Branch Proxy      │         │  Branch Proxy      │
    │  "photogrammetry"  │         │     "coding"       │
    │  ROUTER+DEALER     │         │  ROUTER+DEALER     │
    │  Port: 5551        │         │  Port: 5552        │
    └──────────┬─────────┘         └──────────┬─────────┘
               │                               │
       ┌───────┴───────┐               ┌───────┴───────┐
       │               │               │               │
┌──────▼─────┐  ┌─────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
│   Claude   │  │   Gemini   │  │  DeepSeek  │  │ Researcher │
│  (DEALER)  │  │  (DEALER)  │  │  (DEALER)  │  │  (DEALER)  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘

Message Flow (Intra-Branch):
Claude → Branch Proxy → Gemini (stays within branch, low latency)

Message Flow (Inter-Branch):
DeepSeek → Coding Proxy → Root Router → Photogrammetry Proxy → Claude
```

---

## Alternative 1: XPUB-XSUB Broker

```
                    ┌────────────────────┐
                    │   XPUB-XSUB Broker │
                    │   ┌──────┐         │
                    │   │ XSUB ├─┐       │
                    │   └──────┘ │       │
                    │            ▼       │
                    │   ┌──────┐         │
                    │   │ XPUB │         │
                    │   └──────┘         │
                    └──────────┬─────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
        ┌──────▼─────┐  ┌─────▼──────┐  ┌─────▼──────┐
        │   Claude   │  │   Gemini   │  │  DeepSeek  │
        │   (PUB+SUB)│  │  (PUB+SUB) │  │  (PUB+SUB) │
        └────────────┘  └────────────┘  └────────────┘
             │                │               │
             │ Subscribe:     │ Subscribe:    │ Subscribe:
             │ "photogram.*"  │ "photogram.*" │ "coding.*"
             │ "core.*"       │ "coding.*"    │ "core.*"
             │                │ "core.*"      │

Subscription Forwarding:
Broker learns "photogram.*" has 2 subscribers
Only forwards matching messages to those subscribers
```

**Best For**: Tree of Thoughts topic-based broadcasts

---

## Alternative 2: NATS Cloud-Native

```
                    ┌────────────────────┐
                    │   NATS Server      │
                    │   (Single Binary)  │
                    │   Port: 4222       │
                    └──────────┬─────────┘
                               │
               ┌───────────────┼───────────────┐
               │               │               │
        ┌──────▼─────┐  ┌─────▼──────┐  ┌─────▼──────┐
        │   Claude   │  │   Gemini   │  │  DeepSeek  │
        │ NATS Client│  │NATS Client │  │NATS Client │
        └────────────┘  └────────────┘  └────────────┘

Subjects (instead of branches):
  core.>                    (wildcard: all core topics)
  photogrammetry.mesh.>     (hierarchical)
  photogrammetry.camera.>
  coding.review.>

Claude subscribes to:
  - core.claude
  - photogrammetry.mesh.*
  - photogrammetry.camera.request

Message: "photogrammetry.mesh.update" → Routed to all "photogrammetry.mesh.*" subscribers
```

**Best For**: Simplicity + Cloud deployment

---

## Alternative 3: Shared Memory + UDS (Same Machine)

```
┌─────────────────────────────────────────────────┐
│         Shared Memory Region (mmap)             │
│  ┌────────────────────────────────────────┐    │
│  │  Point Cloud Data (100 MB)             │    │
│  │  [x1,y1,z1, x2,y2,z2, ... xN,yN,zN]   │    │
│  └────────────────────────────────────────┘    │
│         ↑                           ↑           │
│         │ write                read │           │
│    ┌────┴─────┐            ┌────────┴─────┐    │
│    │  Claude  │            │   Gemini     │    │
│    │  Process │            │   Process    │    │
│    └────┬─────┘            └────────┬─────┘    │
│         │                           │           │
│         └───────────┬───────────────┘           │
│                     │                           │
│           ┌─────────▼─────────┐                │
│           │ Unix Domain Socket │                │
│           │ (Control Messages) │                │
│           └────────────────────┘                │
└─────────────────────────────────────────────────┘

Control Flow (via UDS):
Claude → UDS → "pointcloud_ready: offset=0, size=100MB" → Gemini
Gemini reads directly from shared memory (zero-copy)

Data Flow:
Claude writes → Shared Memory ← Gemini reads
(NO kernel copies, NO network stack, pure memory access)
```

**Best For**: Massive point cloud transfers (10-1000 MB)

---

## Alternative 4: gRPC Bidirectional Streaming

```
┌──────────────┐                      ┌──────────────┐
│    Claude    │                      │    Gemini    │
│ gRPC Client  │                      │ gRPC Server  │
└──────┬───────┘                      └──────┬───────┘
       │                                     │
       │ OpenStream("photogrammetry")       │
       ├─────────────────────────────────────>
       │                                     │
       │         StreamID: 123               │
       <─────────────────────────────────────┤
       │                                     │
       │ Message: "analyze mesh v1"          │
       ├─────────────────────────────────────>
       │                                     │
       │       Message: "processing..."      │
       <─────────────────────────────────────┤
       │                                     │
       │ Message: "refine zone A"            │
       ├─────────────────────────────────────>
       │                                     │
       │       Message: "zone A refined"     │
       <─────────────────────────────────────┤
       │                                     │
       │ CloseStream()                       │
       ├─────────────────────────────────────>

Single HTTP/2 connection, multiplexed streams
Both directions send/receive simultaneously
```

**Best For**: Live iterative collaboration

---

## Alternative 5: Kafka Event Stream (Multi-Timeline)

```
        Kafka Cluster
┌───────────────────────────────────────┐
│                                       │
│  Topic: "tot.exploration"             │
│  ┌─────────────────────────────────┐ │
│  │ Partition 0 (Approach A)        │ │
│  │ [E0, E1, E2, E3, ...]           │ │
│  │ Offset: 0 → 1 → 2 → 3           │ │
│  └─────────────────────────────────┘ │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │ Partition 1 (Approach B)        │ │
│  │ [E0, E1, E2, E3, E4, ...]       │ │
│  │ Offset: 0 → 1 → 2 → 3 → 4       │ │
│  └─────────────────────────────────┘ │
│                                       │
│  ┌─────────────────────────────────┐ │
│  │ Partition 2 (Approach C)        │ │
│  │ [E0, E1, E2, ...]               │ │
│  │ Offset: 0 → 1 → 2               │ │
│  └─────────────────────────────────┘ │
└───────────────────────────────────────┘
         ↑           ↑           ↑
         │           │           │
    ┌────┴──┐   ┌───┴────┐  ┌───┴────┐
    │Claude │   │ Gemini │  │DeepSeek│
    │ P0,P1 │   │  P1,P2 │  │  P0,P2 │
    └───────┘   └────────┘  └────────┘

Each partition = independent thought timeline
Agents can replay from any offset
Immutable log persists for days
```

**Best For**: Tree of Thoughts with history replay

---

## Alternative 6: NNG SURVEY Pattern (Consensus)

```
                ┌──────────────┐
                │    Claude    │
                │  (SURVEYOR)  │
                └──────┬───────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
       │  SURVEY: "Should we refine?"  │
       ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│  Gemini  │    │ DeepSeek │    │  GPT-4   │
│(RESPONDENT)   │(RESPONDENT)   │(RESPONDENT)
└─────┬────┘    └─────┬────┘    └─────┬────┘
      │               │               │
      │ Confidence:   │ Confidence:   │ Confidence:
      │    0.85       │    0.92       │    0.78
      │               │               │
      └───────────────┴───────────────┘
                       │
                       ▼
                ┌──────────────┐
                │    Claude    │
                │ Waits for all│
                │ 3 responses  │
                │ Avg: 0.85    │
                │ Decision: GO │
                └──────────────┘

Built-in timeout for non-responsive agents
Automatically aggregates responses
Perfect for voting/quorum scenarios
```

**Best For**: Multi-agent consensus/voting

---

## Alternative 7: Redis MQ (Async Task Queue)

```
           Redis Server
┌────────────────────────────────┐
│                                │
│  Queue: "photogrammetry_tasks" │
│  ┌──────────────────────────┐ │
│  │ [Task1, Task2, Task3]    │ │
│  │   ↑         ↓             │ │
│  │  PUSH      POP            │ │
│  └──────────────────────────┘ │
│                                │
│  Queue: "photogrammetry_results"│
│  ┌──────────────────────────┐ │
│  │ [Result1, Result2]       │ │
│  └──────────────────────────┘ │
└────────────────────────────────┘
         ↑                ↓
         │                │
    ┌────┴────┐      ┌────▼────┐
    │ Claude  │      │ Gemini  │
    │ Producer│      │ Consumer│
    └─────────┘      └─────────┘

Claude's Timeline:
  1. PUSH task to queue
  2. Continue other work (non-blocking)
  3. Later: POP result from result queue

Gemini's Timeline:
  1. BLPOP task (blocking wait)
  2. Process task
  3. PUSH result to result queue
```

**Best For**: Asynchronous work delegation

---

## Topology Comparison

### Star Topology (Current ZMQ)
```
        Agent1
          │
Agent4 ─ Root ─ Agent2
          │
        Agent3
```
- **Pros**: Central routing, easy to monitor
- **Cons**: Root is single point of failure

### Mesh Topology (NATS, NNG)
```
Agent1 ─── Agent2
  │    \  /   │
  │     \/    │
  │     /\    │
  │    /  \   │
Agent4 ─── Agent3
```
- **Pros**: No single point of failure
- **Cons**: More connections, complex routing

### Bus Topology (Shared Memory)
```
Agent1 ─── Bus ─── Agent2 ─── Agent3
            │
         Agent4
```
- **Pros**: Simple, efficient broadcast
- **Cons**: Requires same machine

### Client-Server (gRPC, Redis)
```
Client1 ────┐
            ├─── Server
Client2 ────┘
```
- **Pros**: Simple, well-understood
- **Cons**: Server is bottleneck

---

## Performance Spectrum

```
Latency (lower is better)
─────────────────────────────────────────────────────────────>
│         │      │      │        │         │         │
0.1ms    1ms    5ms   10ms     50ms      100ms     1sec

SharedMem  │      │      │        │         │         │
PAIR       │      │      │        │         │         │
ZMQ/NATS   │      │      │        │         │         │
           │      │      │        │         │         │
           │    gRPC     │        │         │         │
           │    Redis    │        │         │         │
           │             │        │         │         │
           │          RabbitMQ    │         │         │
           │             │        │         │         │
           │             │      Kafka       │         │
           │             │        │    EventSourcing  │
```

```
Complexity (lower is better)
─────────────────────────────────────────────────────────────>
│    │      │       │        │         │
1    2      3       4        5

PAIR │      │       │        │
RPC  │      │       │        │
     │      │       │        │
     │   NATS       │        │
     │   NNG        │        │
     │   XPUB-XSUB  │        │
     │              │        │
     │          RawTCP       │
     │          WebSocket    │
     │          gRPC         │
     │          Redis        │
     │          SharedMem    │
     │                       │
     │                    Kafka
     │                    EventSourcing
```

---

## Scaling Comparison

### 2 Agents (Claude + Gemini)
- **Best**: PAIR (simplest, lowest latency)
- **Overkill**: Kafka, Event Sourcing
- **Consider**: Shared Memory if same machine

### 3-10 Agents
- **Best**: ZMQ ROUTER-DEALER (current), NATS
- **Overkill**: Kafka
- **Consider**: XPUB-XSUB for broadcasts

### 10-100 Agents
- **Best**: NATS, Redis MQ
- **Consider**: Kafka for event history
- **Avoid**: PAIR (too many connections)

### 100+ Agents
- **Best**: Kafka, NATS Supercluster
- **Consider**: Event Sourcing for auditability
- **Avoid**: Anything without horizontal scaling

---

## Data Size Optimization

### Small Messages (<1 KB)
- **Best**: ZeroMQ, NATS (minimal overhead)
- **Avoid**: gRPC (HTTP/2 overhead), Kafka (batching delay)

### Medium Messages (1 KB - 1 MB)
- **Best**: Any architecture works well
- **Optimize**: Use compression (gzip, lz4)

### Large Messages (1 MB - 100 MB)
- **Best**: Shared Memory (zero-copy)
- **Alternative**: Send reference via ZMQ, retrieve from S3/disk
- **Avoid**: Sending through message queue (serialization cost)

### Huge Messages (100 MB - 10 GB)
- **Best**: Object storage reference (S3, MinIO)
- **Control Channel**: ZMQ/NATS sends URL + metadata
- **Data Channel**: Direct download from object store

---

## Failure Mode Comparison

### Network Partition
- **ZMQ**: Silent failure, no auto-reconnect (PAIR, REQ-REP)
- **NATS**: Auto-reconnect, message loss during partition
- **Kafka**: Retains messages, consumer replays after partition heals
- **SharedMem**: N/A (same machine)

### Agent Crash
- **ZMQ**: Messages in-flight lost
- **NATS**: Messages in-flight lost (unless JetStream)
- **Kafka**: All messages retained in log
- **Redis/RabbitMQ**: Messages in queue survive crash

### Broker Crash
- **ZMQ**: No broker (except proxy - rebuild connections)
- **NATS**: Agents reconnect to cluster members
- **Kafka**: Consumer group rebalances to other brokers
- **Redis/RabbitMQ**: Downtime until broker restarts

### Message Corruption
- **ZMQ**: CRC check, corrupted messages dropped
- **NATS**: CRC check, NACK and retry
- **Kafka**: Checksum verification, consumer can retry
- **gRPC**: HTTP/2 checksums, automatic retry

---

## Developer Experience Ranking

### Easiest to Debug (Best to Worst)
1. **PAIR** - Direct connection, see every message
2. **RPC** - Synchronous, stack traces work
3. **NATS** - Simple protocol, good logging
4. **ZMQ ROUTER-DEALER** - Routing adds complexity
5. **gRPC** - HTTP/2 makes Wireshark harder
6. **Redis/RabbitMQ** - Need to inspect queue state
7. **Kafka** - Partitions/offsets add mental overhead
8. **Event Sourcing** - Requires replaying events to understand state

### Best Documentation
1. **gRPC** - Excellent official docs, many examples
2. **RabbitMQ** - Comprehensive tutorials
3. **ZeroMQ** - "The Guide" is legendary
4. **NATS** - Good docs, active community
5. **Kafka** - Good but overwhelming for beginners
6. **NNG** - Sparse but improving
7. **Shared Memory** - Platform-specific, fragmented info

### Fastest to Prototype
1. **PAIR** - 10 lines of code
2. **RPC** - Standard library built-ins
3. **NATS** - Install server, connect, done
4. **ZMQ** - pip install, bind, connect
5. **Redis** - pip install redis, queue operations
6. **gRPC** - .proto file + code generation step
7. **Kafka** - Docker Compose, create topics, etc.

---

## Summary: Which Architecture for Which Scenario?

| Scenario | Best Choice | Alternative |
|----------|-------------|-------------|
| **Current Synaptic Mesh** | Keep ZMQ ROUTER-DEALER | Add NATS option |
| **2-agent photogrammetry** | Shared Memory + UDS | PAIR sockets |
| **Tree of Thoughts broadcasts** | XPUB-XSUB | NATS subjects |
| **Cloud deployment** | gRPC | ZMTP/WebSocket |
| **Agent consensus/voting** | NNG SURVEY | Custom RPC |
| **Async task delegation** | Redis MQ | NATS queue |
| **Learning from history** | Event Sourcing | Kafka |
| **Live collaboration** | gRPC bidirectional | WebSocket |
| **Maximum simplicity** | PAIR | NATS |
| **Maximum performance** | Shared Memory | PAIR |
| **Maximum scalability** | Kafka | NATS supercluster |
| **Maximum reliability** | RabbitMQ | Kafka |

---

## Visual: Message Journey Comparison

### ZeroMQ (Current)
```
Claude → [DEALER socket] → TCP → [Branch ROUTER] → [Branch DEALER] → TCP → [Root ROUTER] → TCP → [Branch DEALER] → [Branch ROUTER] → TCP → [Gemini DEALER]

Steps: 9
Latency: <1ms
```

### NATS
```
Claude → [NATS Client] → TCP → [NATS Server] → TCP → [NATS Client] → Gemini

Steps: 5
Latency: <1ms
```

### Shared Memory
```
Claude → [Write to mmap] → Shared Memory ← [Read from mmap] ← Gemini

Steps: 2
Latency: <0.1ms
```

### gRPC
```
Claude → [gRPC Stub] → HTTP/2 Stream → [gRPC Server] → Gemini

Steps: 4
Latency: 5-10ms
```

### Kafka
```
Claude → [Producer] → TCP → [Kafka Broker] → Disk → [Consumer] → Gemini

Steps: 6
Latency: 10-100ms
```

---

## Decision Matrix (Score out of 10)

|  | Latency | Throughput | Reliability | Simplicity | Scalability | Debug | Elegant | **Total** |
|--|---------|------------|-------------|------------|-------------|-------|---------|-----------|
| **XPUB-XSUB** | 9 | 9 | 6 | 7 | 9 | 7 | 8 | **55** |
| **RPC** | 7 | 6 | 8 | 10 | 4 | 10 | 6 | **51** |
| **Redis MQ** | 9 | 9 | 7 | 7 | 9 | 7 | 7 | **55** |
| **RabbitMQ** | 7 | 7 | 9 | 6 | 9 | 7 | 6 | **51** |
| **Event Sourcing** | 5 | 6 | 10 | 3 | 9 | 9 | 9 | **51** |
| **Kafka** | 4 | 10 | 10 | 2 | 10 | 6 | 8 | **50** |
| **PAIR** | 10 | 10 | 6 | 10 | 2 | 10 | 9 | **57** |
| **Raw TCP** | 10 | 10 | 6 | 5 | 5 | 6 | 4 | **46** |
| **gRPC** | 7 | 7 | 8 | 6 | 8 | 7 | 7 | **50** |
| **ZMTP/WS** | 8 | 7 | 7 | 5 | 7 | 6 | 6 | **46** |
| **NATS** | 9 | 9 | 7 | 9 | 9 | 8 | 9 | **60** ⭐ |
| **NNG** | 9 | 9 | 7 | 8 | 9 | 7 | 8 | **57** |
| **SharedMem+UDS** | 10 | 10 | 7 | 6 | 2 | 5 | 7 | **47** |

**Winner for general-purpose**: NATS (60/70)
**Winner for 2-agent**: PAIR (57/70)
**Winner for same-machine bulk**: Shared Memory (47/70, but 10/10 for specific use case)
