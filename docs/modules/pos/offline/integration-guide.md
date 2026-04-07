# Integration Guide

## Adding Offline Support to a New Feature

### 1. Define offline behavior

Decide which restriction level applies when offline:

| Level       | Behavior                             |
| ----------- | ------------------------------------ |
| `ENABLED`   | Fully functional offline             |
| `DISABLED`  | Not available offline — show overlay |
| `READ_ONLY` | View only, no mutations              |
| `QUEUED`    | Actions accepted but queued for sync |
| `PARTIAL`   | Some sub-features unavailable        |

### 2. Register the feature restriction

In `frontend/hooks/useFeatureRestriction.ts`, add your feature to the `OFFLINE_RESTRICTIONS` map:

```ts
const OFFLINE_RESTRICTIONS: Record<string, RestrictionLevel> = {
  // ... existing
  "my-feature": "QUEUED",
};
```

### 3. Wrap your component

```tsx
import { OfflineRestrictions } from "@/components/pos/offline/OfflineRestrictions";

function MyFeature() {
  return (
    <OfflineRestrictions featureId="my-feature">
      <MyFeatureContent />
    </OfflineRestrictions>
  );
}
```

### 4. Queue transactions

Use `useTransactionQueue` to enqueue operations that need server sync:

```tsx
import { useTransactionQueue } from "@/hooks";

function MyForm() {
  const { enqueue } = useTransactionQueue();

  const handleSubmit = async (data: FormData) => {
    await enqueue({
      id: generateOfflineTransactionId("custom"),
      type: "custom",
      data,
      createdAt: new Date().toISOString(),
    });
  };
}
```

### 5. Cache data for offline access

Add a new entity store in `frontend/lib/offline/stores/` and register it in the cache manager warmup list.

---

## Best Practices

- Always use `generateOfflineTransactionId()` for offline record IDs.
- Keep transaction payloads small — only include data the server needs.
- Handle `useOfflineStatus()` in top-level layouts to show global indicators.
- Test offline flows by disabling network in browser DevTools.

## Common Pitfalls

- **Forgetting to handle the offline case** — Always check `isOnline` before making direct API calls.
- **Circular imports** — Use dynamic `import()` when referencing sync-engine from hooks.
- **Large payloads** — IndexedDB has per-origin storage limits (~50MB typical). Monitor cache size.
