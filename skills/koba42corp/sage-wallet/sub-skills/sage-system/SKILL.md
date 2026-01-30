---
name: sage-system
description: Sage system operations. Sync status, version info, database statistics and maintenance.
---

# Sage System

System status and maintenance operations.

## Endpoints

### Status

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_sync_status` | `{}` | Get sync progress |
| `get_version` | `{}` | Get wallet version |

### Database

| Endpoint | Payload | Description |
|----------|---------|-------------|
| `get_database_stats` | `{}` | Database statistics |
| `perform_database_maintenance` | `{"force_vacuum": false}` | Optimize database |

## Sync Status Response

```json
{
  "balance": "1000000000000",
  "unit": {"decimals": 12, "ticker": "XCH"},
  "synced_coins": 150,
  "total_coins": 150,
  "receive_address": "xch1...",
  "burn_address": "xch1...",
  "unhardened_derivation_index": 100,
  "hardened_derivation_index": 50,
  "checked_files": 25,
  "total_files": 25,
  "database_size": 52428800
}
```

## Version Response

```json
{
  "version": "0.12.7"
}
```

## Database Stats Response

```json
{
  "total_pages": 10000,
  "free_pages": 500,
  "free_percentage": 5.0,
  "page_size": 4096,
  "database_size_bytes": 40960000,
  "free_space_bytes": 2048000,
  "wal_pages": 100
}
```

## Maintenance Response

```json
{
  "vacuum_duration_ms": 1500,
  "analyze_duration_ms": 200,
  "wal_checkpoint_duration_ms": 50,
  "total_duration_ms": 1750,
  "pages_vacuumed": 250,
  "wal_pages_checkpointed": 100
}
```

## Examples

```bash
# Check sync status
sage_rpc get_sync_status '{}'

# Get version
sage_rpc get_version '{}'

# Database stats
sage_rpc get_database_stats '{}'

# Run maintenance
sage_rpc perform_database_maintenance '{"force_vacuum": false}'

# Force full vacuum (slower)
sage_rpc perform_database_maintenance '{"force_vacuum": true}'
```

## Sync Progress

Calculate sync percentage:
```
progress = (synced_coins / total_coins) * 100
```

Check if synced:
```
synced = (synced_coins == total_coins)
```

## Notes

- Run maintenance periodically to reclaim space
- `force_vacuum` does full database compaction (slower but more thorough)
- Large `wal_pages` indicates pending writes; checkpoint clears them
