# API Reference

## React Hooks

### `useOfflineStatus()`

Monitor connection status in React components.

```ts
const { status, isOnline } = useOfflineStatus();
// status: 'ONLINE' | 'OFFLINE' | 'SYNCING' | 'SYNC_ERROR'
// isOnline: boolean
```

### `useTransactionQueue()`

Manage the offline transaction queue.

```ts
const { queue, pendingCount, failedCount, enqueue, retry, exportQueue, importQueue } = useTransactionQueue();
```

### `useManualSync()`

Trigger manual sync operations.

```ts
const { trigger, cancel, loading, progress, currentEntity, lastResult, error } = useManualSync();
await trigger("full"); // 'push' | 'pull' | 'full' | 'forcePush' | 'resetSync'
```

### `useSyncHistory()`

Access sync log entries with filtering.

```ts
const { entries, loading, filters, setFilters, exportLogs, clearHistory } = useSyncHistory();
```

### `useSyncToasts()`

Display sync-related notifications.

```ts
const { toasts, dismiss, showSuccess, showError, showConnectionLost, showConnectionRestored } = useSyncToasts();
```

### `useCacheRefresh()`

Refresh cached data from server.

```ts
const { trigger, cancel, loading, progress, currentEntity, error, lastRefresh } = useCacheRefresh();
await trigger("products", "merge"); // entity, strategy
```

### `useFeatureRestriction(featureId)`

Check offline restrictions for a feature.

```ts
const { restriction, isRestricted, canAccess } = useFeatureRestriction("reports");
// restriction: 'ENABLED' | 'DISABLED' | 'READ_ONLY' | 'QUEUED' | 'PARTIAL'
```

### `useCacheWarmup()`

Warm up the local cache on app startup.

```ts
const { warmup, loading, progress } = useCacheWarmup();
```

---

## Service Classes

### `syncEngine` (singleton)

```ts
import { syncEngine } from "@/lib/offline/sync-engine";

await syncEngine.init();
await syncEngine.manualSync();
syncEngine.destroy();
```

### `connectionMonitor` (singleton)

```ts
import { connectionMonitor } from "@/lib/offline/connection-monitor";

connectionMonitor.startMonitoring();
const status = connectionMonitor.getStatus();
connectionMonitor.stopMonitoring();
```

### `conflictResolver` (singleton)

```ts
import { conflictResolver } from "@/lib/offline/conflict-resolver";

const conflicts = await conflictResolver.detectConflicts(localData, serverData);
const result = await conflictResolver.resolveConflict(conflict, "server-wins");
```

### `syncAnalytics` (singleton)

```ts
import { syncAnalytics } from "@/lib/offline/sync-analytics";

syncAnalytics.trackSyncStart(context);
const report = syncAnalytics.generateReport("week");
```

### `TransactionQueue` (class)

```ts
import { TransactionQueue } from "@/lib/offline/transaction-queue";

const queue = new TransactionQueue();
await queue.enqueue(transaction);
const pending = await queue.getPending();
```

### `IDBService` (singleton)

```ts
import { IDBService } from "@/lib/offline/indexeddb";

const db = IDBService.getInstance();
await db.init();
await db.put("products", product);
```
