---
name: redis
description: Redis database management. Key-value operations, caching, pub/sub, and data structure commands.
metadata: {"clawdbot":{"emoji":"🔴","always":true,"requires":{"bins":["curl","jq"]}}}
---

# Redis 🔴

Redis in-memory database management.

## Setup

```bash
export REDIS_URL="redis://localhost:6379"
```

## Features

- Key-value operations
- Data structures (lists, sets, hashes)
- Pub/Sub messaging
- Cache management
- TTL management

## Usage Examples

```
"Get key user:123"
"Set cache for 1 hour"
"Show all keys matching user:*"
"Flush cache"
```

## Commands

```bash
redis-cli GET key
redis-cli SET key value EX 3600
redis-cli KEYS "pattern*"
```
