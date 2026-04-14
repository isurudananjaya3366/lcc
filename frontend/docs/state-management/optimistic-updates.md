# Optimistic Updates

## Pattern

`useUpdateProduct` demonstrates the standard optimistic update lifecycle:

1. **onMutate** — cancel in-flight queries, snapshot current data,
   apply optimistic change
2. **onError** — rollback to snapshot
3. **onSettled** — re-fetch regardless of outcome

```ts
onMutate: async ({ id, updates }) => {
  await queryClient.cancelQueries({ queryKey: productKeys.detail(id) });
  const previous = queryClient.getQueryData(productKeys.detail(id));
  queryClient.setQueryData(productKeys.detail(id), { ...previous, ...updates });
  return { previous };
},
onError: (_err, _vars, context) => {
  queryClient.setQueryData(productKeys.detail(id), context.previous);
},
onSettled: () => {
  queryClient.invalidateQueries({ queryKey: productKeys.detail(id) });
},
```

## When to Use

- List → detail page (single item updates)
- Toggling boolean fields (favourite, active)
- Quantity / price adjustments in cart

## When NOT to Use

- File uploads or complex server-side transformations
- Operations that change related resources significantly
- First-time creation (no existing data to snapshot)
