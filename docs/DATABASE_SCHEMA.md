# Database Schema Design

## Overview
SQLite database for persistent storage of messages, users, raids, parties, and guilds. Optimized for real-time queries and high-frequency inserts.

---

## Tables

### users
Stores user account information and profile data.

```sql
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  email TEXT,
  password_hash TEXT,
  avatar_url TEXT,
  badge TEXT,
  level INTEGER DEFAULT 1,
  experience INTEGER DEFAULT 0,
  server_id TEXT NOT NULL,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login DATETIME,
  is_active BOOLEAN DEFAULT 1,

  FOREIGN KEY (server_id) REFERENCES servers(id),
  CHECK (level >= 1 AND level <= 120)
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_server_id ON users(server_id);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_level ON users(level);
```

**Fields:**
- `id`: UUID or numeric ID (system generated)
- `username`: Display name (unique per server)
- `email`: Contact email
- `password_hash`: Bcrypt hash (never store plain password)
- `avatar_url`: Profile picture CDN URL
- `badge`: admin, moderator, vip, standard
- `level`: Character level (1-120)
- `experience`: Total experience points
- `server_id`: FK to servers table
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update
- `last_login`: Most recent connection
- `is_active`: Account active flag

---

### messages
High-volume table for all chat messages.

```sql
CREATE TABLE messages (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  user_id TEXT NOT NULL,
  server_id TEXT NOT NULL,
  channel_id TEXT,
  content TEXT NOT NULL,
  metadata JSON,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT 0,
  deletion_reason TEXT,

  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (server_id) REFERENCES servers(id),
  FOREIGN KEY (channel_id) REFERENCES channels(id),
  CHECK (type IN ('user', 'system', 'dm', 'raid', 'party', 'guild'))
);

CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_server_id ON messages(server_id);
CREATE INDEX idx_messages_channel_id ON messages(channel_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_type ON messages(type);
CREATE INDEX idx_messages_search ON messages(content);
CREATE INDEX idx_messages_composite ON messages(server_id, created_at DESC);
```

**Fields:**
- `id`: UUID (globally unique message ID)
- `type`: Message category (user, system, dm, raid, party, guild)
- `user_id`: FK to users table (sender)
- `server_id`: FK to servers table
- `channel_id`: FK to channels (optional for non-channel messages)
- `content`: Message text
- `metadata`: JSON for type-specific data
- `created_at`: Sent timestamp
- `updated_at`: Last edit timestamp
- `is_deleted`: Soft delete flag
- `deletion_reason`: Why message was deleted

---

### servers
Represents a game server or realm.

```sql
CREATE TABLE servers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  region TEXT NOT NULL,
  capacity INTEGER DEFAULT 1000,
  current_population INTEGER DEFAULT 0,
  status TEXT DEFAULT 'online',

  language TEXT DEFAULT 'en',
  pvp_enabled BOOLEAN DEFAULT 1,
  level_range_min INTEGER DEFAULT 1,
  level_range_max INTEGER DEFAULT 120,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  CHECK (status IN ('online', 'maintenance', 'offline')),
  CHECK (current_population <= capacity)
);

CREATE INDEX idx_servers_region ON servers(region);
CREATE INDEX idx_servers_status ON servers(status);
```

**Fields:**
- `id`: Server identifier
- `name`: Server display name
- `region`: Geographic region
- `capacity`: Max concurrent players
- `current_population`: Online player count
- `status`: online, maintenance, offline
- `language`: Default language
- `pvp_enabled`: PvP mode flag
- `level_range_min/max`: Level restrictions

---

### channels
Chat channels within a server.

```sql
CREATE TABLE channels (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  server_id TEXT NOT NULL,
  description TEXT,
  visibility TEXT DEFAULT 'public',
  category TEXT,

  min_level INTEGER DEFAULT 1,
  message_count INTEGER DEFAULT 0,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (server_id) REFERENCES servers(id),
  CHECK (visibility IN ('public', 'private', 'restricted'))
);

CREATE INDEX idx_channels_server_id ON channels(server_id);
CREATE INDEX idx_channels_name ON channels(name);
```

**Fields:**
- `id`: Channel UUID
- `name`: Channel name (e.g., "general", "raids")
- `server_id`: FK to servers
- `description`: Channel purpose
- `visibility`: public, private, restricted
- `category`: Channel category/folder
- `min_level`: Minimum character level to access
- `message_count`: Running total of messages

---

### raids
Raid group events and state.

```sql
CREATE TABLE raids (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  boss_name TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  server_id TEXT NOT NULL,
  leader_id TEXT NOT NULL,

  status TEXT DEFAULT 'preparing',
  health_percentage INTEGER DEFAULT 100,
  start_time DATETIME,
  end_time DATETIME,
  duration_seconds INTEGER,

  participant_count INTEGER DEFAULT 0,
  victory BOOLEAN,
  loot_generated BOOLEAN DEFAULT 0,

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (server_id) REFERENCES servers(id),
  FOREIGN KEY (leader_id) REFERENCES users(id),
  CHECK (status IN ('preparing', 'in_progress', 'wipe', 'victory')),
  CHECK (difficulty IN ('normal', 'hard', 'mythic')),
  CHECK (health_percentage >= 0 AND health_percentage <= 100)
);

CREATE INDEX idx_raids_server_id ON raids(server_id);
CREATE INDEX idx_raids_leader_id ON raids(leader_id);
CREATE INDEX idx_raids_status ON raids(status);
CREATE INDEX idx_raids_created_at ON raids(created_at DESC);
```

**Fields:**
- `id`: Raid instance UUID
- `name`: Raid name/title
- `boss_name`: Boss entity name
- `difficulty`: normal, hard, mythic
- `server_id`: FK to servers
- `leader_id`: Raid leader FK
- `status`: preparing, in_progress, wipe, victory
- `health_percentage`: Boss health %
- `start_time`: When raid began
- `end_time`: When raid ended
- `duration_seconds`: Total duration
- `participant_count`: Number of players
- `victory`: Success flag
- `loot_generated`: Rewards distributed

---

### raid_participants
Many-to-many relationship for raid members.

```sql
CREATE TABLE raid_participants (
  raid_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT NOT NULL,
  class TEXT NOT NULL,
  damage_dealt INTEGER DEFAULT 0,
  healing INTEGER DEFAULT 0,
  damage_taken INTEGER DEFAULT 0,
  deaths INTEGER DEFAULT 0,
  uptime_percentage INTEGER DEFAULT 100,

  PRIMARY KEY (raid_id, user_id),
  FOREIGN KEY (raid_id) REFERENCES raids(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  CHECK (role IN ('tank', 'dps', 'healer')),
  CHECK (uptime_percentage >= 0 AND uptime_percentage <= 100)
);

CREATE INDEX idx_raid_participants_user_id ON raid_participants(user_id);
```

**Fields:**
- `raid_id`: FK to raids
- `user_id`: FK to users
- `role`: tank, dps, healer
- `class`: Character class
- `damage_dealt`: Total damage dealt
- `healing`: Total healing done
- `damage_taken`: Total damage taken
- `deaths`: Number of deaths
- `uptime_percentage`: % of raid alive

---

### parties
Player grouping for cooperative play.

```sql
CREATE TABLE parties (
  id TEXT PRIMARY KEY,
  name TEXT,
  leader_id TEXT NOT NULL,
  server_id TEXT NOT NULL,

  member_count INTEGER DEFAULT 1,
  max_members INTEGER DEFAULT 5,
  status TEXT DEFAULT 'active',

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  disbanded_at DATETIME,

  FOREIGN KEY (leader_id) REFERENCES users(id),
  FOREIGN KEY (server_id) REFERENCES servers(id),
  CHECK (status IN ('active', 'disbanded'))
);

CREATE INDEX idx_parties_leader_id ON parties(leader_id);
CREATE INDEX idx_parties_server_id ON parties(server_id);
```

**Fields:**
- `id`: Party UUID
- `name`: Party name (optional)
- `leader_id`: Party leader FK
- `server_id`: FK to servers
- `member_count`: Current members
- `max_members`: Party size limit
- `status`: active, disbanded
- `disbanded_at`: When party ended

---

### party_members
Party membership tracking.

```sql
CREATE TABLE party_members (
  party_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  role TEXT DEFAULT 'member',
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (party_id, user_id),
  FOREIGN KEY (party_id) REFERENCES parties(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  CHECK (role IN ('leader', 'member'))
);

CREATE INDEX idx_party_members_user_id ON party_members(user_id);
```

---

### guilds
Player-run organizations.

```sql
CREATE TABLE guilds (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  server_id TEXT NOT NULL,
  leader_id TEXT NOT NULL,

  level INTEGER DEFAULT 1,
  treasury_balance INTEGER DEFAULT 0,
  member_count INTEGER DEFAULT 1,
  max_members INTEGER DEFAULT 500,

  territory TEXT,
  conquest_points INTEGER DEFAULT 0,
  war_status TEXT DEFAULT 'peace',

  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (server_id) REFERENCES servers(id),
  FOREIGN KEY (leader_id) REFERENCES users(id),
  CHECK (level >= 1 AND level <= 50),
  CHECK (war_status IN ('peace', 'active_war', 'conquered'))
);

CREATE INDEX idx_guilds_server_id ON guilds(server_id);
CREATE INDEX idx_guilds_leader_id ON guilds(leader_id);
```

**Fields:**
- `id`: Guild UUID
- `name`: Guild name (unique)
- `server_id`: FK to servers
- `leader_id`: Guild master FK
- `level`: Guild level (1-50)
- `treasury_balance`: Guild bank gold
- `member_count`: Current members
- `max_members`: Member capacity
- `territory`: Conquered territory
- `conquest_points`: Points toward conquest
- `war_status`: peace, active_war, conquered

---

### guild_members
Guild membership with roles.

```sql
CREATE TABLE guild_members (
  guild_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  rank TEXT DEFAULT 'member',
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  contribution INTEGER DEFAULT 0,

  PRIMARY KEY (guild_id, user_id),
  FOREIGN KEY (guild_id) REFERENCES guilds(id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  CHECK (rank IN ('leader', 'officer', 'member'))
);

CREATE INDEX idx_guild_members_user_id ON guild_members(user_id);
```

---

### direct_messages
1-to-1 private messages.

```sql
CREATE TABLE direct_messages (
  id TEXT PRIMARY KEY,
  from_user_id TEXT NOT NULL,
  to_user_id TEXT NOT NULL,
  content TEXT NOT NULL,

  is_read BOOLEAN DEFAULT 0,
  read_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (from_user_id) REFERENCES users(id),
  FOREIGN KEY (to_user_id) REFERENCES users(id)
);

CREATE INDEX idx_dm_from_user_id ON direct_messages(from_user_id);
CREATE INDEX idx_dm_to_user_id ON direct_messages(to_user_id);
CREATE INDEX idx_dm_is_read ON direct_messages(is_read);
CREATE INDEX idx_dm_created_at ON direct_messages(created_at DESC);
```

---

### sessions
Active user sessions for tracking.

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  server_id TEXT NOT NULL,
  ip_address TEXT,
  user_agent TEXT,

  login_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  logout_at DATETIME,
  last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (server_id) REFERENCES servers(id)
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_server_id ON sessions(server_id);
CREATE INDEX idx_sessions_login_at ON sessions(login_at DESC);
```

---

## Indexes Summary

| Table | Index | Purpose |
|-------|-------|---------|
| messages | idx_messages_created_at | Recent message retrieval |
| messages | idx_messages_composite | Live log queries |
| messages | idx_messages_user_id | User message lookup |
| messages | idx_messages_search | Full-text search |
| users | idx_users_created_at | User history |
| raids | idx_raids_created_at | Raid history |
| parties | idx_parties_leader_id | Leader's parties |
| guilds | idx_guilds_server_id | Server guilds |

---

## Query Patterns

### Recent Messages (Live Log)
```sql
SELECT * FROM messages
WHERE server_id = ? AND created_at > ?
ORDER BY created_at DESC
LIMIT 100;
```

### User Messages
```sql
SELECT * FROM messages
WHERE user_id = ? AND server_id = ?
ORDER BY created_at DESC
LIMIT 50;
```

### Search Messages
```sql
SELECT * FROM messages
WHERE server_id = ?
  AND content LIKE ?
ORDER BY created_at DESC
LIMIT 50;
```

### Active Raids
```sql
SELECT * FROM raids
WHERE server_id = ? AND status IN ('preparing', 'in_progress')
ORDER BY created_at DESC;
```

### User Statistics
```sql
SELECT
  u.id,
  u.username,
  COUNT(m.id) as message_count,
  COUNT(DISTINCT rp.raid_id) as raid_count,
  u.level,
  u.last_login
FROM users u
LEFT JOIN messages m ON u.id = m.user_id
LEFT JOIN raid_participants rp ON u.id = rp.user_id
WHERE u.server_id = ?
GROUP BY u.id
ORDER BY message_count DESC;
```

---

## Performance Optimization

### Partitioning Strategy
For high-volume tables, consider date-based partitioning:
```sql
-- Partition messages by month
CREATE TABLE messages_2025_12 AS
SELECT * FROM messages
WHERE created_at >= '2025-12-01'
  AND created_at < '2026-01-01';
```

### Archive Strategy
- Keep recent messages (last 90 days) in active table
- Archive older messages to separate tables/database
- Maintain composite indexes on server_id + created_at

### Batch Operations
- Use batch inserts for multiple messages
- Batch update player stats every 5 minutes
- Defer non-critical updates to off-peak hours

---

## Backup Strategy

- Daily full backup at 2 AM UTC
- Hourly incremental backups
- Keep 30 days of backups
- Replicate to secondary location
- Test restore procedures monthly

---

## Migration Path

```sql
-- v1.0 → v1.1
ALTER TABLE messages ADD COLUMN edited_at DATETIME;
ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0;
CREATE TABLE message_reactions (
  message_id TEXT,
  user_id TEXT,
  reaction TEXT,
  PRIMARY KEY (message_id, user_id, reaction),
  FOREIGN KEY (message_id) REFERENCES messages(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Monitoring Queries

### Table Sizes
```sql
SELECT name, COUNT(*) as row_count
FROM sqlite_master m
JOIN (SELECT COUNT(*) FROM messages) WHERE m.type='table'
GROUP BY name;
```

### Index Usage
```sql
EXPLAIN QUERY PLAN
SELECT * FROM messages WHERE server_id = '1' AND created_at > '2025-12-03'
ORDER BY created_at DESC LIMIT 100;
```

### Slow Queries (>1000ms)
Track in application logs, flag for index optimization.
