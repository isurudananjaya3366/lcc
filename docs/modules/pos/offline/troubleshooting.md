# Troubleshooting

## Common Issues

### Offline mode stuck on

**Symptom:** The UI shows "Offline" even though the network is connected.

**Solutions:**

1. Check that the backend server is running and accessible.
2. The health ping endpoint (`/api/pos/sync/health`) may be down — verify with `curl`.
3. Clear browser cache and reload.
4. Check browser console for CORS or SSL errors on the ping request.

### Transactions not syncing

**Symptom:** Pending count stays non-zero after going online.

**Solutions:**

1. Check the sync engine is initialized (`syncEngine.init()` called on startup).
2. Look for sync lock issues — the lock may be stuck. Wait for auto-expire (5 min) or use "Reset Sync State".
3. Verify the push endpoint returns 2xx responses.
4. Check for authentication errors (401) — the session may have expired.

### Sync fails repeatedly

**Symptom:** Transactions move to "failed" status after multiple retries.

**Solutions:**

1. Check the error message on failed transactions via `SyncLogViewer`.
2. Verify server-side validation — the transaction payload may be invalid.
3. Try "Force Push" from the manual sync menu.
4. Export transactions and contact support if the issue persists.

### Product not found in cache

**Symptom:** Search returns no results while offline.

**Solutions:**

1. Cache may not have been warmed up — use "Refresh Cache" button.
2. The product may have been added after the last cache warmup.
3. Cache limit may have evicted the product — check cache configuration.

### Data seems lost

**Symptom:** Transactions appear to be missing after sync.

**Solutions:**

1. Check the sync history log for errors.
2. Synced transactions are cleaned up after 24 hours — they may have been removed from the local queue.
3. Verify on the server that transactions were received (check server-assigned IDs).

---

## Debugging Techniques

### Browser DevTools

1. **Application > IndexedDB** — Inspect `lcc_pos_cache` database and object stores.
2. **Application > Service Workers** — Check SW registration and status.
3. **Network tab** — Monitor sync API calls and responses.
4. **Console** — Look for `[SyncEngine]`, `[ConnectionMonitor]`, `[TransactionQueue]` log prefixes.

### Export Diagnostic Data

```ts
import { syncAnalytics } from "@/lib/offline/sync-analytics";
const report = syncAnalytics.generateReport("week");
console.log(JSON.stringify(report, null, 2));
```

### Force Reset

As a last resort, clear IndexedDB entirely:

```ts
indexedDB.deleteDatabase("lcc_pos_cache");
```

Then refresh the page and re-initialize the cache.
