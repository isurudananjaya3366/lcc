# Transaction Queue

## Purpose

The transaction queue stores all operations made while offline and manages their lifecycle from creation through sync to cleanup.

## Transaction Structure

```ts
interface QueuedTransaction {
  id: string; // Offline ID (OFFLINE-{TYPE}-{TS}-{SEQ})
  type: string; // 'sale' | 'customer' | 'inventory_adjustment'
  status: string; // 'pending' | 'synced' | 'failed'
  data: unknown; // Transaction payload
  createdAt: string; // ISO timestamp
  syncedAt?: string; // When synced
  serverId?: string; // Server-assigned ID
  retryCount: number; // Failure retry count
  errorMessage?: string; // Last error
  dependsOn?: string[]; // Parent transaction IDs
}
```

## Offline ID Format

```
OFFLINE-SALE-1737674400000-001
OFFLINE-CUST-1737674401000-002

Format: OFFLINE-{TYPE}-{TIMESTAMP}-{SEQUENCE}
```

- **TYPE**: Transaction category prefix (SALE, CUST, INVADJ)
- **TIMESTAMP**: Unix epoch milliseconds
- **SEQUENCE**: Auto-incrementing counter per session

## Queue Operations API

| Method                  | Description                         |
| ----------------------- | ----------------------------------- |
| `enqueue(tx)`           | Add transaction to queue            |
| `getPending()`          | Get all pending transactions (FIFO) |
| `getFailed()`           | Get failed transactions             |
| `getCount()`            | Get pending transaction count       |
| `markSynced(id)`        | Mark as synced with server ID       |
| `markFailed(id, error)` | Mark as failed, increment retry     |
| `retry(id)`             | Re-enqueue a failed transaction     |
| `exportQueue()`         | Export as JSON for backup           |
| `importQueue(data)`     | Import from JSON backup             |
| `cleanup(threshold)`    | Remove old synced transactions      |

## Persistence

Transactions are stored in IndexedDB (`transactions` object store) and survive page refreshes and browser restarts.

## Cleanup Policy

Synced transactions older than 24 hours are eligible for automatic cleanup. Failed transactions are retained indefinitely until manually resolved.
