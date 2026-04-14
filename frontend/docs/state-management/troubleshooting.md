# Troubleshooting

## Common Issues

### Store not persisting

- Check that `persist: true` is passed to `createStore`.
- Ensure `localStorage` is available (SSR won't have it).
- Verify the `partialize` function includes the fields you expect.

### Stale data after mutation

- Confirm `invalidateCache` is called in `onSuccess` or `onSettled`.
- Check that the query key passed matches the key factory output.
- Use **RELATED** invalidation strategy if changes affect other modules.

### Hydration mismatch

- Wrap client-only content with `useHydration()`:
  ```tsx
  const hydrated = useHydration();
  if (!hydrated) return null;
  ```

### Infinite re-renders from Zustand

- Use `useShallow` when selecting multiple fields:
  ```ts
  const { a, b } = useMyStore(useShallow((s) => ({ a: s.a, b: s.b })));
  ```

### Query not firing

- Verify `enabled` is `true` (for detail hooks, check that `id` is defined).
- Check that the `QueryProvider` wraps the component tree.

### DevTools not showing stores

- Install the Redux DevTools browser extension.
- Zustand devtools middleware maps store names like `LCC/UI`.
- TanStack Query DevTools panel is separate (bottom of screen).
