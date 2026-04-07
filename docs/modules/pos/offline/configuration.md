# Configuration

## Environment Variables

| Variable                     | Type    | Default | Description                 |
| ---------------------------- | ------- | ------- | --------------------------- |
| `NEXT_PUBLIC_ENABLE_OFFLINE` | boolean | `true`  | Enable/disable offline mode |

## Sync Engine Settings

| Setting              | Type   | Default | Description                     |
| -------------------- | ------ | ------- | ------------------------------- |
| `DEFAULT_BATCH_SIZE` | number | 50      | Transactions per sync batch     |
| `MAX_BATCH_SIZE`     | number | 100     | Maximum batch size              |
| `SYNC_TIMEOUT`       | number | 120000  | Sync operation timeout (ms)     |
| `SYNC_LOCK_TIMEOUT`  | number | 300000  | Lock auto-release timeout (ms)  |
| `AUTO_SYNC_INTERVAL` | number | 300000  | Auto-sync interval (ms)         |
| `MIN_SYNC_COOLDOWN`  | number | 60000   | Minimum time between syncs (ms) |
| `PING_TIMEOUT`       | number | 5000    | Health check timeout (ms)       |

## Cache Settings

| Setting              | Type   | Default | Description                    |
| -------------------- | ------ | ------- | ------------------------------ |
| `cache.maxProducts`  | number | 1000    | Maximum products in IndexedDB  |
| `cache.maxCustomers` | number | 500     | Maximum customers in IndexedDB |

## Retry / Backoff Settings

| Setting              | Type   | Default | Description                            |
| -------------------- | ------ | ------- | -------------------------------------- |
| `retry.maxAttempts`  | number | 5       | Maximum retry attempts per transaction |
| `retry.baseDelay`    | number | 60000   | Initial retry delay (ms)               |
| `retry.maxDelay`     | number | 960000  | Maximum retry delay (ms)               |
| `retry.jitterFactor` | number | 0.25    | Jitter range (± percentage)            |

## Conflict Resolution Settings

| Setting                       | Type   | Default       | Description                     |
| ----------------------------- | ------ | ------------- | ------------------------------- |
| `conflict.defaultStrategy`    | string | `server-wins` | Default resolution strategy     |
| `PRICE_CHANGE_THRESHOLD_AUTO` | number | 0.05          | Auto-resolve price changes ≤ 5% |

## API Endpoints

| Endpoint               | Method | Description               |
| ---------------------- | ------ | ------------------------- |
| `PUSH_ENDPOINT`        | POST   | Push offline transactions |
| `PULL_ENDPOINT`        | GET    | Pull server updates       |
| `HEALTH_PING_ENDPOINT` | GET    | Connection Health check   |

## Performance Tuning

- **Reduce batch size** if sync operations time out on slow connections.
- **Increase auto-sync interval** to reduce server load in high-traffic environments.
- **Lower cache limits** on devices with limited storage.
