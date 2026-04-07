# Conflict Resolution

## Conflict Detection

Conflicts are detected when pushed transactions or pulled updates have overlapping modifications to the same entity. Detection checks:

1. **Version mismatch** — Local version ≠ server version.
2. **Concurrent modification** — Both local and server modified the same fields since last sync.
3. **Delete vs. update** — One side deleted, the other updated.
4. **Stock conflicts** — Inventory quantity changed on both sides.
5. **Price conflicts** — Price changed beyond threshold simultaneously.

## Conflict Types

| Type     | Trigger                                                 |
| -------- | ------------------------------------------------------- |
| `update` | Same entity modified locally and on server              |
| `delete` | Entity deleted on one side, updated on the other        |
| `stock`  | Inventory quantity conflict                             |
| `price`  | Price changed beyond `PRICE_CHANGE_THRESHOLD_AUTO` (5%) |

## Resolution Strategies

| Strategy        | Behavior                              | Use Case                |
| --------------- | ------------------------------------- | ----------------------- |
| **Server Wins** | Discard local changes, accept server  | Default for most fields |
| **Client Wins** | Keep local changes, reject server     | User preferences        |
| **Merge**       | Combine non-conflicting field changes | Non-overlapping edits   |
| **Manual**      | Prompt user via conflict modal        | Critical business data  |

### Stock Conflict Resolution

Delta-based: The resolver computes the net change on each side and applies both deltas to the base value, preventing double-counting.

### Price Conflict Resolution

- Price change ≤ 5%: auto-resolve with server value
- Price change > 5%: flag for manual resolution

## Audit Trail

Every resolution generates an `AuditTrailEntry` recording:

- Original local and server values
- Strategy used
- Resulting merged value
- Resolution timestamp
- User who resolved (if manual)

## UI Components

- **SyncConflictModal** — Side-by-side comparison with resolution radio buttons.
- **OfflineRestrictions** — Wraps features that have limited capability offline.
