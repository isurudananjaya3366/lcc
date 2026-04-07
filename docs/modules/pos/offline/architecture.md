# Architecture — POS Offline Mode

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  POS Terminal UI                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Sales Form   │  │ Product List │  │ Sync UI  │  │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  │
└─────────┼──────────────────┼───────────────┼────────┘
          │                  │               │
          ▼                  ▼               ▼
┌─────────────────────────────────────────────────────┐
│              Offline Mode Manager                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Connection   │  │ Transaction  │  │ Sync     │  │
│  │ Monitor      │  │ Queue        │  │ Engine   │  │
│  └──────┬───────┘  └──────┬───────┘  └────┬─────┘  │
└─────────┼──────────────────┼───────────────┼────────┘
          │                  │               │
          ▼                  ▼               ▼
┌─────────────────────────────────────────────────────┐
│                  IndexedDB Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │ Products     │  │ Customers    │  │ Queue    │  │
│  │ Store        │  │ Store        │  │ Store    │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────┘
```

## Component Interaction

| Component              | Responsibility                            | Depends On                                   |
| ---------------------- | ----------------------------------------- | -------------------------------------------- |
| **Connection Monitor** | Detect online/offline/quality             | Browser APIs, server ping                    |
| **Transaction Queue**  | Store and manage pending transactions     | IndexedDB                                    |
| **Sync Engine**        | Orchestrate push/pull/conflict resolution | Queue, Connection Monitor, Conflict Resolver |
| **Conflict Resolver**  | Detect and resolve data conflicts         | —                                            |
| **Cache Manager**      | Warm up, clear, and manage cached data    | IndexedDB, entity stores                     |
| **Sync Analytics**     | Track metrics, generate reports           | —                                            |

## Data Flow

```
                  OFFLINE                    ONLINE
                  ───────                    ──────
 User Action ──► Queue Transaction ──► [Stored in IndexedDB]
                                              │
                    connection restored ───────┘
                                              │
                                              ▼
                                       Acquire Sync Lock
                                              │
                                              ▼
                                       Push Transactions ──► Server API
                                              │
                                              ▼
                                       Pull Updates     ◄── Server API
                                              │
                                              ▼
                                       Resolve Conflicts
                                              │
                                              ▼
                                       Update Local Cache
                                              │
                                              ▼
                                       Release Lock
```

## Technology Stack

| Layer      | Technology                                                |
| ---------- | --------------------------------------------------------- |
| Storage    | IndexedDB via IDBService singleton                        |
| Messaging  | BroadcastChannel (`pos-sync-channel`)                     |
| Background | Service Worker (`public/sw.js`)                           |
| State      | React hooks (useOfflineStatus, useTransactionQueue, etc.) |
| UI         | React + Tailwind CSS with dark mode                       |

## Design Decisions

1. **IndexedDB over localStorage** — Structured data, larger storage limits, async API.
2. **Singleton services** — Single connection monitor, sync engine, and IDB service to prevent resource contention.
3. **Offline-first IDs** — `OFFLINE-{TYPE}-{TS}-{SEQ}` format enables creating records without server roundtrip.
4. **Delta-based stock resolution** — Stock conflicts use delta arithmetic rather than absolute values to preserve concurrent adjustments.
5. **Exponential backoff with jitter** — Retry failures progressively with randomization to avoid thundering herd.
