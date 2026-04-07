# Sync Engine

## Sync Flow

```
Connection Detected → Acquire Lock → Push Transactions → Pull Updates → Resolve Conflicts → Update Cache → Release Lock
```

## Connection Detection

The `ConnectionMonitor` checks connectivity via:

1. `navigator.onLine` browser API
2. Server health ping to `HEALTH_PING_ENDPOINT`
3. Latency measurement for connection quality assessment

Quality levels: `excellent` (< 100ms), `good` (< 300ms), `fair` (< 1000ms), `poor` (≥ 1000ms).

## Push Operations

Pending transactions are pushed in batches (default `50`, max `100`). Each batch is sent to `PUSH_ENDPOINT` and the server responds with assigned IDs for each transaction.

## Pull Operations

After pushing, the engine pulls server updates since `lastSyncTimestamp` from `PULL_ENDPOINT`. Paginated responses are supported. Pulled data is compared against local cache for conflicts.

## Batch Optimization

| Setting              | Default |
| -------------------- | ------- |
| `DEFAULT_BATCH_SIZE` | 50      |
| `MAX_BATCH_SIZE`     | 100     |
| `SYNC_TIMEOUT`       | 120s    |

Transactions are grouped by type within each batch to optimize server-side processing.

## Sync Lock

Only one sync can run at a time. The lock auto-expires after `SYNC_LOCK_TIMEOUT` (5 minutes) to prevent deadlocks.

## Auto-Sync

Auto-sync runs every `AUTO_SYNC_INTERVAL` (5 minutes) when online. A minimum cooldown of `MIN_SYNC_COOLDOWN` (60 seconds) prevents rapid re-sync.

## Error Handling & Retries

Exponential backoff with jitter:

| Attempt | Base Delay   | With Jitter |
| ------- | ------------ | ----------- |
| 1       | 1 min        | 45s – 75s   |
| 2       | 2 min        | 90s – 150s  |
| 3       | 4 min        | 3m – 5m     |
| 4       | 8 min        | 6m – 10m    |
| 5+      | 16 min (cap) | 12m – 20m   |

Maximum retry attempts: 5 per transaction.

## Configuration

See [configuration.md](configuration.md) for all tunable settings.
