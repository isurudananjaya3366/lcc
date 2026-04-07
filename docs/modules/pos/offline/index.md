# POS Offline Mode — Technical Documentation

> **Module:** POS Offline Mode  
> **Phase:** 05 — ERP Core Modules Part 2  
> **SubPhase:** 02 — POS Offline Mode

---

## Overview

The POS Offline Mode module enables point-of-sale terminals to continue operating when internet connectivity is lost. Transactions are queued locally, data is cached in IndexedDB, and a sync engine handles bidirectional synchronization when connectivity is restored.

### Key Features

- **Offline Transaction Processing** — Complete sales, create customers, and adjust inventory without internet.
- **Local Data Caching** — Products, customers, and settings cached in IndexedDB for instant access.
- **Automatic Sync** — Queued transactions sync automatically when connectivity returns.
- **Conflict Resolution** — Server-wins, client-wins, merge, and manual strategies for data conflicts.
- **Connection Monitoring** — Real-time detection of online/offline transitions with quality assessment.
- **Emergency Export** — Export queued transactions as JSON for backup and cross-device recovery.

### Quick Start

```ts
import { syncEngine } from "@/lib/offline/sync-engine";
import { useOfflineStatus } from "@/hooks/useOfflineStatus";

// Initialize the sync engine on app startup
await syncEngine.init();

// In a React component
function POSTerminal() {
  const { isOnline, status } = useOfflineStatus();
  // ...
}
```

---

## Documentation Pages

| Page                                             | Description                          |
| ------------------------------------------------ | ------------------------------------ |
| [architecture.md](architecture.md)               | System architecture and data flow    |
| [indexeddb.md](indexeddb.md)                     | IndexedDB schema and CRUD operations |
| [transaction-queue.md](transaction-queue.md)     | Queue management and offline IDs     |
| [sync-engine.md](sync-engine.md)                 | Sync engine, batching, and retries   |
| [conflict-resolution.md](conflict-resolution.md) | Conflict detection and resolution    |
| [api-reference.md](api-reference.md)             | React hooks and service APIs         |
| [configuration.md](configuration.md)             | Settings, tuning, and environment    |
| [integration-guide.md](integration-guide.md)     | Developer integration guide          |
| [troubleshooting.md](troubleshooting.md)         | Common issues and debugging          |
| [user-guide.md](user-guide.md)                   | Operator / end-user guide            |

---

## Prerequisites

- Browser with IndexedDB and Service Worker support (Chrome 80+, Firefox 78+, Edge 80+)
- `NEXT_PUBLIC_ENABLE_OFFLINE=true` in environment
- Backend API endpoints for sync (`/api/pos/sync/push`, `/api/pos/sync/pull`, `/api/pos/sync/health`)
