# POS Developer Guide

## Development Setup

```bash
# Prerequisites
node >= 18
pnpm >= 8

# Install dependencies
cd frontend
pnpm install

# Start development server
pnpm dev

# Access POS at http://localhost:3000/pos
```

## Project Structure

```
frontend/
├── app/(pos)/pos/           ← POS route group (full-screen layout)
├── components/modules/pos/  ← All POS components
├── services/pos.ts          ← API service layer
├── stores/pos/cart.ts       ← Zustand cart store
├── lib/pos/                 ← Utilities (tax, calculator)
└── types/                   ← Shared TypeScript types
```

## Adding a New Component

1. Create file in the appropriate subdirectory under `components/modules/pos/`
2. Add `'use client';` directive (all POS components are client-side)
3. Define TypeScript interface for props
4. Export from the directory's `index.ts` barrel file
5. Import and use in parent component

## State Management

### Cart Store (Zustand)

```typescript
import { useCartStore } from "@/stores/pos/cart";

// In component:
const { items, addItem, removeItem, getGrandTotal } = useCartStore();
```

### POS Context (React Context)

```typescript
import { usePOS } from "../context/POSContext";

// In component:
const { openModal, closeModal, currentShift, heldSales } = usePOS();
```

## API Integration

All API calls go through `services/pos.ts`:

```typescript
import { posService } from "@/services/pos";

// Search products
const results = await posService.searchProducts("rice");

// Open session
const session = await posService.openSession("default", 10000);
```

**Important:** `api.get()` accepts only an endpoint string (no options object). `api.post()` accepts endpoint + data.

## TypeScript

```bash
# Run type check
npx tsc --noEmit

# With pretty errors disabled (for CI)
npx tsc --noEmit --pretty false
```

## Common Patterns

### Immer Draft Types

When spreading Immer draft objects in Zustand, cast explicitly:

```typescript
state.items[idx] = { ...(existing as POSCartItem), quantity: newQty };
```

### Currency Formatting

```typescript
amount.toLocaleString("en-LK", { minimumFractionDigits: 2 });
// or use:
import { formatCurrency } from "@/lib/pos/totalCalculator";
```

### Dialog Components

Use `Dialog` from shadcn/ui. **Do NOT use AlertDialog** (it doesn't exist in this project). Use `ConfirmDialog` from `@/components/ui/confirm-dialog` for confirmation dialogs.

## Testing

```bash
# Backend tests (Docker)
docker compose exec backend bash -c \
  'DJANGO_SETTINGS_MODULE=config.settings.test_pg python -m pytest tests/ -q'

# Frontend TypeScript check
cd frontend && npx tsc --noEmit
```
