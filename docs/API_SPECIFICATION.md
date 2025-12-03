# Backend API Specification

## Overview

Core WebSocket API for real-time message streaming and live log functionality. Designed for high-frequency message delivery with low latency and reliable reconnection handling.

---

## Connection

### Endpoint
```
ws://localhost:8000/ws/live-log
```

### Authentication
Currently unsecured for development. Production will require:
- JWT token in connection header
- API key in query parameter
- OAuth2 token bearer

### Connection Example
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/live-log?token=YOUR_TOKEN');

ws.onopen = () => {
  console.log('Connected');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};

ws.onerror = (error) => {
  console.error('Connection error:', error);
};

ws.onclose = () => {
  console.log('Connection closed');
};
```

---

## Message Types

### 1. User Message
```json
{
  "type": "user",
  "id": "msg_uuid_1234",
  "timestamp": "2025-12-03T12:00:00.000Z",
  "user_id": "user_12345",
  "username": "DragonMaster",
  "user_avatar": "https://api.example.com/avatars/user_12345.png",
  "user_badge": "admin",
  "content": "Message text here",
  "metadata": {
    "server": "main",
    "channel": "general",
    "level": 50
  }
}
```

### 2. System Message
```json
{
  "type": "system",
  "id": "sys_uuid_5678",
  "timestamp": "2025-12-03T12:00:00.000Z",
  "event": "user_joined",
  "data": {
    "user_id": "user_12345",
    "username": "DragonMaster",
    "count_online": 245
  },
  "severity": "info"
}
```

**System Events:**
- `user_joined` - User entered the server
- `user_left` - User disconnected
- `user_leveled_up` - Character level increase
- `raid_started` - Raid event initiated
- `server_maintenance` - Maintenance window
- `error` - System error occurred

### 3. Direct Message
```json
{
  "type": "dm",
  "id": "dm_uuid_9012",
  "timestamp": "2025-12-03T12:00:00.000Z",
  "from_user_id": "user_12345",
  "from_username": "DragonMaster",
  "to_user_id": "user_67890",
  "content": "Private message text",
  "read": false
}
```

### 4. Raid Message
```json
{
  "type": "raid",
  "id": "raid_uuid_3456",
  "timestamp": "2025-12-03T12:00:00.000Z",
  "raid_id": "raid_001",
  "raid_name": "Dragon's Lair",
  "boss_name": "Ancient Red Dragon",
  "difficulty": "mythic",
  "participants": [
    {
      "user_id": "user_12345",
      "username": "DragonMaster",
      "role": "tank",
      "class": "warrior"
    }
  ],
  "status": "in_progress",
  "health_percentage": 45,
  "duration_seconds": 324
}
```

**Raid Statuses:**
- `preparing` - Raid forming
- `in_progress` - Active raid
- `wipe` - Group defeated
- `victory` - Boss defeated

### 5. Party Message
```json
{
  "type": "party",
  "id": "party_uuid_7890",
  "timestamp": "2025-12-03T12:00:00.000Z",
  "party_id": "party_123",
  "leader_id": "user_12345",
  "leader_name": "DragonMaster",
  "member_count": 4,
  "event": "member_joined",
  "event_data": {
    "member_id": "user_99999",
    "member_name": "NewAdventurer"
  }
}
```

**Party Events:**
- `member_joined` - New member added
- `member_left` - Member removed
- `member_promoted` - Member promoted to leader
- `disbanded` - Party ended
- `level_bonus` - Party bonus triggered

### 6. Guild Message
```json
{
  "type": "guild",
  "id": "guild_uuid_2345",
  "timestamp": "2025-12-03T12:00:00.000Z",
  "guild_id": "guild_001",
  "guild_name": "The Dragonslayers",
  "guild_level": 25,
  "event": "conquest_complete",
  "event_data": {
    "territory": "Dragon Valley",
    "points_earned": 5000,
    "rank_change": "Tier 2 → Tier 1"
  }
}
```

**Guild Events:**
- `member_joined` - New guild member
- `member_left` - Member departed
- `conquest_started` - Territory conquest began
- `conquest_complete` - Territory claimed
- `upgrade_complete` - Guild upgraded
- `war_declared` - Guild war started
- `treasury_deposit` - Funds added

---

## Client Commands

### Subscribe to Message Type
```json
{
  "action": "subscribe",
  "message_types": ["user", "raid"]
}
```

### Unsubscribe from Message Type
```json
{
  "action": "unsubscribe",
  "message_types": ["dm"]
}
```

### Request Message History
```json
{
  "action": "get_history",
  "limit": 100,
  "offset": 0,
  "filters": {
    "type": "user",
    "user_id": "user_12345",
    "channel": "general"
  }
}
```

**Response:**
```json
{
  "action": "history",
  "messages": [...],
  "total_count": 5000,
  "limit": 100,
  "offset": 0
}
```

### Heartbeat (Keep-Alive)
```json
{
  "action": "ping"
}
```

**Response:**
```json
{
  "action": "pong",
  "timestamp": "2025-12-03T12:00:00.000Z"
}
```

### Search Messages
```json
{
  "action": "search",
  "query": "dragon",
  "filters": {
    "type": "user",
    "user_id": "user_12345",
    "date_from": "2025-12-01T00:00:00Z",
    "date_to": "2025-12-03T23:59:59Z"
  }
}
```

**Response:**
```json
{
  "action": "search_results",
  "query": "dragon",
  "results": [...],
  "count": 42
}
```

---

## Server Events

### Connection Established
```json
{
  "action": "connected",
  "connection_id": "conn_uuid_1234",
  "message": "Successfully connected to live log"
}
```

### Connection Closed
```json
{
  "action": "disconnected",
  "reason": "normal_closure|connection_timeout|protocol_error|server_error"
}
```

### Error
```json
{
  "action": "error",
  "error_code": 1002,
  "error_message": "Protocol Error",
  "details": {
    "field": "message_type",
    "issue": "Invalid message type"
  }
}
```

**Error Codes:**
- `1000` - Normal closure
- `1001` - Going away
- `1002` - Protocol error
- `1003` - Unsupported data
- `1006` - Abnormal closure
- `1008` - Policy violation
- `1009` - Message too big
- `1011` - Server error
- `4000` - Authentication failed
- `4001` - Invalid token
- `4002` - Token expired
- `4003` - Rate limit exceeded

### Rate Limit Warning
```json
{
  "action": "rate_limit",
  "current_requests": 95,
  "limit": 100,
  "window_seconds": 60,
  "reset_in_seconds": 35
}
```

---

## Rate Limiting

**Per Connection:**
- 100 messages per 60 seconds
- 10 commands per 60 seconds
- 1000 connections per IP

**Backoff Strategy:**
```
Attempt 1: Immediate
Attempt 2: Wait 1 second
Attempt 3: Wait 2 seconds
Attempt 4: Wait 4 seconds
Attempt 5: Wait 8 seconds
Attempt 6+: Wait 60 seconds (max)
```

---

## Latency Requirements

- **Connection Establishment:** < 500ms
- **Message Delivery:** < 100ms (p95)
- **Search Query:** < 500ms
- **History Fetch:** < 1000ms

---

## Message Flow Diagram

```
Client                                    Server
  |                                         |
  |--- WebSocket Connect ----------------->|
  |                                         |
  |<-- Connected Event -------------------|
  |                                         |
  |--- Subscribe to [user, raid] -------->|
  |                                         |
  |<-- User Message 1 -------------------|
  |<-- User Message 2 -------------------|
  |<-- Raid Message ----------------------|
  |<-- User Message 3 -------------------|
  |                                         |
  |--- Heartbeat/Ping ------------------>|
  |<-- Pong ------------------------------|
  |                                         |
  |--- Get History (last 100) -------->|
  |<-- History Response ------------------|
  |                                         |
  |--- Search "dragon" ----------------->|
  |<-- Search Results -------------------|
  |                                         |
  |<-- [Continuous Message Stream] ------|
  |                                         |
  |--- WebSocket Close ----------------->|
  |<-- Disconnected Event --------------|
```

---

## Performance Considerations

### Pagination
Always use pagination for large result sets:
```json
{
  "action": "get_history",
  "limit": 50,
  "offset": 0
}
```

### Filtering
Use server-side filters to reduce payload:
```json
{
  "action": "get_history",
  "filters": {
    "type": "raid",
    "date_from": "2025-12-03T00:00:00Z"
  }
}
```

### Selective Subscriptions
Only subscribe to needed message types:
```json
{
  "action": "subscribe",
  "message_types": ["user", "raid"]
}
```
Avoid subscribing to all types if not needed.

### Connection Pooling
- Maintain single connection per client
- Don't open multiple connections
- Reuse existing connection for multiple operations

---

## Security

### Current Status (Development)
- No authentication required
- All messages publicly visible
- No rate limiting enforced

### Production Requirements
- OAuth2 authentication
- Rate limiting per IP/user
- Message encryption
- DDoS protection
- SQL injection prevention
- XSS prevention
- CSRF protection

---

## Testing Checklist

- [ ] Connection establishment within 500ms
- [ ] Message delivery latency < 100ms (p95)
- [ ] Graceful reconnection after disconnect
- [ ] Exponential backoff on connection failure
- [ ] Heartbeat keeps connection alive
- [ ] Search performance < 500ms for typical queries
- [ ] History pagination works correctly
- [ ] Message filtering accurate
- [ ] Rate limiting enforced
- [ ] Error messages clear and actionable

---

## Changelog

### v1.0 (Current)
- Initial WebSocket API
- 6 message types: user, system, dm, raid, party, guild
- Client subscription system
- Message history retrieval
- Search functionality
- Heartbeat mechanism

### v1.1 (Planned)
- Authentication and authorization
- Message encryption
- Advanced filtering
- Analytics endpoint
- Admin commands
- Message persistence (database)

---

## Support

For API questions or issues:
1. Check this documentation
2. Review error codes and messages
3. Check server logs for details
4. Test with WebSocket client tools (wscat, websocat)
