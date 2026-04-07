# Shared Resources

## Overview

This directory contains shared TypeScript type definitions and constants used across multiple frontend applications in the LankaCommerce Cloud platform (POS, Webstore, Dashboard).

### What Belongs Here

| Include | Exclude |
|---------|---------|
| Entity types (Product, Order) | App-specific types |
| Status enums | Component props |
| API response types | Internal implementation types |
| Validation schemas | App configuration |
| Sri Lanka constants | Environment variables |

---

## Directory Structure

```
shared/
├── constants/       # Shared constant values, enums, and configuration
│   └── .gitkeep
├── types/           # Shared TypeScript interfaces and type definitions
│   └── .gitkeep
└── README.md        # This file
```

### `types/`

Shared TypeScript interfaces and types consumed by multiple frontend apps:

- Entity types (Product, Order, Customer)
- API request/response types
- Common utility types
- Enum types

### `constants/`

Shared constant values and enums consumed by multiple frontend apps:

- Status enums (OrderStatus, PaymentStatus)
- Configuration constants
- Sri Lanka-specific constants (currency, timezone, districts)
- Common validation rules

---

## Usage

### Importing Shared Types

```typescript
// From any frontend app (POS, Webstore, Dashboard)
import { Product, Order } from '@/shared/types';
```

### Importing Shared Constants

```typescript
// From any frontend app
import { ORDER_STATUS, CURRENCY } from '@/shared/constants';
```

### Path Alias Configuration

Each frontend app requires a path alias in its `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/shared/*": ["../../shared/*"]
    }
  }
}
```

---

## Guidelines

- **Single Source of Truth:** Define types and constants once, import everywhere.
- **TypeScript Only:** This directory is for TypeScript definitions; backend (Python/Django) has its own type system.
- **Naming Conventions:** Use PascalCase for types/interfaces, UPPER_SNAKE_CASE for constants.
- **Barrel Exports:** Each subdirectory should have an `index.ts` that re-exports all public members.
- **No App-Specific Code:** Only place resources here that are used by **two or more** frontend apps.
