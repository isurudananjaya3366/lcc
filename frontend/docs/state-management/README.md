# State Management

Documentation for the LankaCommerce Cloud POS state management layer.

## Architecture

- **Zustand** — lightweight client state (UI, Auth)
- **TanStack Query** — server/async state (CRUD, caching, mutations)
- **Immer** — immutable state updates via mutable syntax

## Contents

| Guide | Description |
|-------|-------------|
| [Stores](./stores.md) | Zustand store patterns and conventions |
| [Queries](./queries.md) | TanStack Query hook patterns |
| [Mutations](./mutations.md) | Mutation hooks and side-effects |
| [Cache Management](./cache-management.md) | Invalidation strategies |
| [Optimistic Updates](./optimistic-updates.md) | Optimistic UI patterns |
| [Infinite Queries](./infinite-queries.md) | Paginated / infinite scroll |
| [DevTools](./devtools.md) | Browser DevTools integration |
| [Best Practices](./best-practices.md) | Guidelines and conventions |
| [Troubleshooting](./troubleshooting.md) | Common issues and fixes |
| [Testing](./testing.md) | Testing state and queries |
