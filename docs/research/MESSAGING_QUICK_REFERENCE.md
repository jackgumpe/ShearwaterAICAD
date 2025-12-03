# Messaging Architecture Quick Reference
**Date**: 2025-11-28

## One-Line Summary of Each Architecture

1. **XPUB-XSUB**: Dynamic broker that forwards subscription-filtered messages - best for topic-based broadcast
2. **RPC/Request-Reply**: Synchronous call-and-response - best for verification dialogues
3. **Redis MQ**: In-memory message queue with sub-millisecond latency - best for async task delegation
4. **RabbitMQ**: Persistent message queue with delivery guarantees - best for reliable async workflows
5. **Event Sourcing**: Immutable event log enabling replay - best for learning from agent history
6. **Kafka**: Distributed stream log with partitions - best for multi-timeline reasoning
7. **PAIR**: Direct 1-to-1 bidirectional socket - best for hotline between two agents
8. **Raw TCP**: Custom protocol with zero abstraction - best for LLM-specific optimizations
9. **gRPC**: HTTP/2-based RPC with bidirectional streaming - best for live collaboration
10. **ZMTP/WebSocket**: ZeroMQ semantics over firewall-friendly transport - best for cloud deployment
11. **NATS**: Lightweight cloud-native pub-sub with request-reply - best for simplicity + performance
12. **NNG**: Modern scalability protocols with SURVEY pattern - best for agent consensus
13. **SharedMem+UDS**: Zero-copy IPC for same-machine - best for massive point cloud transfers

---

## Decision Tree

```
START
  │
  ├─ Same machine?
  │    YES → Shared Memory + Unix Domain Sockets (7x faster)
  │    NO → Continue
  │
  ├─ Only 2 agents forever?
  │    YES → PAIR sockets (simplest, lowest latency)
  │    NO → Continue
  │
  ├─ Need message history/replay?
  │    YES → Kafka or Event Sourcing
  │    NO → Continue
  │
  ├─ Agents need to work offline?
  │    YES → Redis MQ or RabbitMQ
  │    NO → Continue
  │
  ├─ Through firewall/cloud?
  │    YES → WebSocket hybrid or gRPC
  │    NO → Continue
  │
  ├─ Tree of Thoughts broadcasts?
  │    YES → XPUB-XSUB or NATS
  │    NO → Continue
  │
  ├─ Want simplicity?
  │    YES → NATS (ZeroMQ alternative)
  │    NO → ZeroMQ ROUTER-DEALER (current)
```

---

## Top 3 Recommendations

### 1. Keep Current + Add Shared Memory (Hybrid)
- **Keep**: ZeroMQ ROUTER-DEALER for routing/control
- **Add**: Shared memory for bulk data (point clouds >10MB)
- **Result**: Best of both worlds - flexible routing + extreme performance

### 2. Migrate to NATS (Strategic)
- **Why**: 90% of ZeroMQ performance, 50% of complexity
- **When**: If ZeroMQ maintenance/debugging becomes burden
- **How**: Gradual migration via wrapper API

### 3. Add XPUB-XSUB Proxy (Tactical)
- **Why**: Tree of Thoughts needs efficient broadcasts
- **When**: Implementing multi-branch thought exploration
- **How**: Single proxy added to existing mesh

---

## Latency Rankings (Best to Worst)

1. Shared Memory + Unix Domain Sockets: <0.1ms
2. PAIR sockets: <1ms
3. Raw TCP / NATS / NNG / XPUB-XSUB: <1ms
4. ZMTP/WebSocket: 1-5ms
5. gRPC: 5-10ms
6. Redis MQ: <1ms (but depends on queue depth)
7. RabbitMQ: 1-10ms
8. Kafka / Event Sourcing: 10-100ms

---

## Complexity Rankings (Simplest to Most Complex)

1. PAIR sockets: 1/5
2. RPC/Request-Reply: 1/5
3. NATS: 2/5
4. NNG: 2/5
5. XPUB-XSUB: 2/5
6. Raw TCP: 3/5
7. ZMTP/WebSocket: 3/5
8. gRPC: 4/5
9. Redis MQ: 4/5
10. Shared Memory: 4/5
11. RabbitMQ: 4/5
12. Event Sourcing: 5/5
13. Kafka: 5/5

---

## Dark Horse Winners

### Shared Memory + Unix Domain Sockets
- **67% latency reduction** vs TCP localhost
- **7x throughput increase**
- **Zero memory copies** for bulk data
- **Perfect for photogrammetry point clouds**

### NATS
- **Cloud-native** alternative to ZeroMQ
- **18MB binary** (vs Kafka's GB-scale deployment)
- **Runs on Raspberry Pi** to data centers
- **40+ language clients**
- **Request-reply built-in**

### NNG SURVEY Pattern
- **Agent consensus** in one pattern
- **Cleaner API** than ZeroMQ
- **Active development** by Scalability Protocols community
- **Perfect for voting/quorum** scenarios

---

## Anti-Patterns for This Use Case

### Don't Use Kafka If...
- You have <10 agents
- You don't need multi-day message retention
- Sub-10ms latency is critical
- You can't dedicate ops resources to cluster management

### Don't Use Raw TCP If...
- You value development speed over control
- Your team lacks low-level networking expertise
- You need advanced patterns (pub-sub, routing)

### Don't Use RabbitMQ If...
- You need sub-millisecond latency
- Message persistence isn't critical
- You prefer simpler infrastructure (use Redis/NATS instead)

---

## Benchmark Targets (What to Measure)

If testing alternatives, measure these metrics:

1. **P50/P99 Latency**: 50th and 99th percentile message delivery time
2. **Throughput**: Messages per second at saturation
3. **Memory Overhead**: Bytes per message in queues/buffers
4. **CPU Usage**: Percent CPU for routing/serialization
5. **Reconnection Time**: How fast agents reconnect after disconnect
6. **Message Loss Rate**: Messages dropped under load
7. **Developer Velocity**: Hours to implement + debug feature

---

## Migration Safety Checklist

Before switching from ZeroMQ to alternative:

- [ ] Run both systems in parallel for 1 week
- [ ] Compare latency distributions (not just averages)
- [ ] Test failure scenarios (network partition, crash, OOM)
- [ ] Measure message loss under load
- [ ] Verify agent reconnection behavior
- [ ] Check log/debug output quality
- [ ] Assess operational complexity (deployment, monitoring)
- [ ] Benchmark CPU/memory overhead
- [ ] Get team consensus on API ergonomics

---

## Quick Wins (No Architecture Change)

Optimizations for current ZeroMQ setup:

1. **Enable Zero-Copy** for messages >4KB (ZMQ_ZERO_COPY_RECV)
2. **Tune HWM** (High Water Mark) per agent message rate
3. **Use IPC transport** for same-machine agents (vs TCP localhost)
4. **Connection Pooling** for frequent reconnects
5. **Message Batching** for high-frequency small messages
6. **Async I/O** for non-blocking receives with timeout

---

## Code Snippet: Hybrid Shared Memory Pattern

```python
# For bulk data (point clouds >10MB)
import mmap
import posix_ipc

class SharedMemoryChannel:
    def __init__(self, name, size=100*1024*1024):  # 100MB
        self.shm = posix_ipc.SharedMemory(name, flags=posix_ipc.O_CREAT, size=size)
        self.buf = mmap.mmap(self.shm.fd, size)

    def write_pointcloud(self, data: bytes):
        """Zero-copy write for large point clouds"""
        self.buf[:len(data)] = data

    def read_pointcloud(self, size: int) -> bytes:
        """Zero-copy read"""
        return self.buf[:size]

# Use with ZeroMQ for control messages
zmq_client.send_message(to="gemini", type="pointcloud_ready",
                        content={"shm_name": "claude_pointcloud", "size": 50_000_000})
```

---

## When to Revisit This Analysis

Triggers to re-evaluate architecture:

- Adding 10+ agents (test NATS vs current ZeroMQ)
- Deploying to cloud/multi-region (test gRPC/WebSocket)
- Latency >5ms P99 (test Shared Memory, PAIR)
- Message loss >0.1% (test Redis/RabbitMQ persistence)
- Ops burden high (test NATS simplicity)
- Need agent conversation replay (test Kafka/Event Sourcing)

---

## Further Reading

- **ZeroMQ Guide**: https://zguide.zeromq.org/
- **NATS Documentation**: https://docs.nats.io/
- **Shared Memory IPC Paper**: TZC for Robotics (arXiv:1810.00556)
- **gRPC vs REST**: https://www.altexsoft.com/blog/what-is-grpc/
- **Kafka Deep Dive**: https://www.hellointerview.com/learn/system-design/deep-dives/kafka
