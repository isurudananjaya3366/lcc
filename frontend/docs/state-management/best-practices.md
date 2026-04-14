# Best Practices

## State Placement

| Data Kind | Where | Example |
|-----------|-------|---------|
| Server data | TanStack Query | Products, orders |
| UI state | Zustand | Sidebar, theme |
| Form state | React state / react-hook-form | Input values |
| URL state | Next.js router | Filters, pagination |

## Do

- Use query key factories — never hand-write keys.
- Keep stores small and focused (one per domain).
- Persist only what is needed across page reloads.
- Use `useShallow` when selecting multiple fields to avoid
  unnecessary re-renders.
- Always register store `reset()` with `registerStoreReset`.
- Use `enabled` to conditionally run queries.
- Use `placeholderData: (prev) => prev` instead of deprecated
  `keepPreviousData`.

## Don't

- Don't duplicate server data in Zustand.
- Don't fetch inside `useEffect` — use TanStack Query hooks.
- Don't use `queryClient.fetchQuery` when `useQuery` works.
- Don't invalidate everything — use targeted strategies.
- Don't store derived data — compute it with selectors.
