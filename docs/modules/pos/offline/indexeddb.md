# IndexedDB Implementation

## Database

| Property | Value           |
| -------- | --------------- |
| Name     | `lcc_pos_cache` |
| Version  | `1`             |

## Object Stores

| Store          | Key Path | Description                  |
| -------------- | -------- | ---------------------------- |
| `products`     | `id`     | Cached product catalog       |
| `customers`    | `id`     | Cached customer records      |
| `transactions` | `id`     | Offline transaction queue    |
| `settings`     | `key`    | POS configuration cache      |
| `categories`   | `id`     | Product categories           |
| `sync_meta`    | `key`    | Sync timestamps and metadata |

## CRUD Operations

```ts
import { IDBService } from "@/lib/offline/indexeddb";

const db = IDBService.getInstance();
await db.init();

// Create / Update
await db.put("products", { id: "p-1", name: "Widget", price: 500 });

// Read
const product = await db.get("products", "p-1");

// Read all
const allProducts = await db.getAll("products");

// Delete
await db.delete("products", "p-1");

// Clear store
await db.clear("products");
```

## Cache Management

- **Warmup**: `CacheManager.warmupCache(['products', 'customers'])` pre-fetches server data.
- **Clear**: `CacheManager.clearAllCaches()` removes all cached data.
- **Size limits**: Configured via constants — default 1000 products, 500 customers.
- **LRU eviction**: Oldest-accessed entries removed when limits are reached.

## Version Upgrades

Schema changes are applied via `upgradeDatabaseSchema()` in `schema.ts`. The upgrade handler runs inside the `onupgradeneeded` callback and creates/modifies object stores as needed.
