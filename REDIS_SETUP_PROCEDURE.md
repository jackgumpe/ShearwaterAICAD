# REDIS SETUP PROCEDURE - PHASE 1 DAY 1

**Status**: BLOCKED - Docker not available
**Date**: 2025-12-02
**Blocker**: Docker not installed on system
**Workaround**: Using Python Redis mock for Phase 1 development

---

## OPTION 1: PROPER REDIS SETUP (When Docker is available)

### Prerequisites:
- Docker Desktop installed on Windows
- Port 6379 available
- Administrator access

### Step 1: Pull Redis Image
```bash
docker pull redis:latest
```

### Step 2: Run Redis Container
```bash
docker run -d --name shearwater-redis -p 6379:6379 redis:latest
```

### Step 3: Verify Redis is Running
```bash
docker ps | grep redis
```

### Step 4: Test Connection
```bash
redis-cli ping
```
Expected output: `PONG`

### Step 5: Verify Persistence
```bash
# Push a message
redis-cli LPUSH test_queue "test_message"

# Verify it persists
redis-cli RPOP test_queue
# Expected: "test_message"
```

---

## OPTION 2: WORKAROUND FOR PHASE 1 DEVELOPMENT

Since Docker is not available, we'll use a Python-based Redis client with a mock/fallback mode:

### Implementation:
1. Use `redis-py` library (already installed)
2. Fallback to in-memory queue if Redis is unavailable
3. Document expected behavior for when Redis becomes available
4. Verify message atomicity in fallback mode

### Step 1: Check if redis-py is installed
```bash
pip list | grep redis
# If not installed: pip install redis
```

### Step 2: Test Redis Connection (with fallback)
```python
import redis

try:
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print("Redis is running")
except:
    print("Redis not available - using fallback mode")
    # Use in-memory queue as fallback
```

---

## CURRENT STATUS - PHASE 1 DAY 1

### What's Done:
- [x] ACE tier definitions locked (133 lines, ready for 100% tagging)
- [x] Emergence signals documented (6 signals with real examples)
- [x] Agent project sync system operational (file read/write/execute verified)

### What's Blocked:
- [ ] Redis setup (Docker not installed)
  - **Impact**: Message queue persistence using Redis
  - **Workaround**: Using in-memory fallback
  - **Next Step**: Install Docker Desktop when available

### What's Next:
1. Continue with in-memory queue fallback for now
2. Document all Redis operations for migration when Docker is available
3. Verify atomicity with fallback implementation
4. Test message flow (5 messages sent, 5 received)

---

## REDIS INTEGRATION PLAN

### For Phase 1:
- Use Python Redis client with fallback to in-memory deque
- Mock Redis behavior for testing
- Document all LPUSH/RPOP operations for later migration

### For Week 2:
- Install Docker Desktop
- Migrate to actual Redis container
- Verify production behavior matches fallback testing

### Success Criteria:
- All messages processed atomically
- Zero message loss in both modes
- Clean migration path when Docker becomes available

---

## MESSAGES QUEUED FOR REDIS

These operations need to work atomically:
1. Agent writes file -> LPUSH to Redis queue
2. Other agent receives notification -> RPOP from Redis queue
3. Verify message integrity after pop

Total queued operations: 5
Expected completion time: Fallback mode testing ~30 minutes

---

## NOTES FOR LATER

When Docker is installed:
1. Run: `docker pull redis:latest`
2. Run: `docker run -d -p 6379:6379 redis:latest`
3. Verify: `redis-cli ping` -> `PONG`
4. Test: `redis-cli LPUSH test "message"` -> `redis-cli RPOP test`
5. Update persistence_daemon.py to use real Redis instead of fallback

---

**Current Workaround Status**: READY
**Fallback Mode**: ACTIVE
**Real Redis**: PENDING (Docker installation needed)

