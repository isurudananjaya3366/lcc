# LankaCommerce Cloud Webstore — Project Structure

## Overview

The LankaCommerce Cloud Webstore is the customer-facing e-commerce storefront for Sri Lankan businesses, built on Next.js 15 with the App Router, React 19, TypeScript, Zustand state management, and TailwindCSS.

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | Next.js 15 (App Router) |
| UI | React 19, TailwindCSS 4, shadcn/ui |
| State | Zustand 5 (with Immer, Persist, DevTools) |
| Data Fetching | TanStack Query 5 |
| API Client | Axios with interceptors |
| Language | TypeScript (strict) |
| Locale | en-LK, Asia/Colombo, LKR (₨) |

## Route Structure

The storefront uses Next.js route groups under `app/(storefront)/`:

| Route | Description |
|---|---|
| `/` | Homepage — hero, featured products, categories |
| `/products` | Product listing with filters/sort |
| `/products/[slug]` | Product detail page |
| `/categories/[slug]` | Category product listing |
| `/cart` | Shopping cart |
| `/checkout` | Checkout flow |
| `/account` | Customer account dashboard |
| `/search?q=` | Search results |

## Directory Structure

```
frontend/
├── app/(storefront)/          # Storefront routes
│   ├── layout.tsx             # Store layout (header + footer)
│   ├── page.tsx               # Homepage
│   ├── loading.tsx            # Loading skeleton
│   ├── error.tsx              # Error boundary
│   ├── not-found.tsx          # 404 page
│   ├── fonts.ts               # Inter + JetBrains Mono
│   ├── products/page.tsx      # Product listing
│   ├── cart/page.tsx          # Cart page
│   ├── checkout/page.tsx      # Checkout page
│   ├── account/page.tsx       # Account page
│   └── search/page.tsx        # Search results
├── components/
│   ├── storefront/            # Store-specific components
│   │   ├── layout/            # StoreHeader, StoreFooter, StoreNavigation
│   │   └── providers/         # ThemeProvider, CartProvider, AuthProvider
│   └── shared/                # Components shared across ERP & store
├── config/                    # Configuration files
│   ├── contact.config.ts      # Business contact info
│   ├── shipping.config.ts     # Zones, rates, free shipping threshold
│   ├── payment.config.ts      # COD, PayHere, bank transfer, Stripe
│   ├── seo.config.ts          # SEO defaults, structured data
│   └── image.config.ts        # Sizes, CDN, upload restrictions
├── hooks/queries/             # TanStack Query hooks
│   ├── useStoreProducts.ts    # Product query hooks
│   └── useStoreCategories.ts  # Category query hooks
├── lib/
│   ├── store/                 # Store configuration & utilities
│   │   ├── config.ts          # Store info, API, currency, locale
│   │   ├── routes.ts          # Route definitions, breadcrumbs
│   │   ├── navigation.ts      # Nav items (main, footer, account)
│   │   ├── social.ts          # Social media links
│   │   └── utils/             # Utility functions
│   │       ├── currency.ts    # LKR formatting, parsing
│   │       ├── price.ts       # Price display, discount badges
│   │       ├── discount.ts    # Discount calculators
│   │       ├── images.ts      # Image URLs, CDN, srcsets
│   │       ├── urls.ts        # Product/category URL builders
│   │       ├── cart.ts        # Cart total calculations
│   │       └── stock.ts       # Stock status checking
│   ├── api/store/             # Store API client
│   │   ├── client.ts          # Axios instance
│   │   ├── config.ts          # Environment detection
│   │   ├── interceptors/      # Auth & error interceptors
│   │   └── modules/           # API modules per domain
│   ├── storeQueryKeys.ts      # TanStack Query key factory
│   ├── storeColorTokens.ts    # Color design tokens
│   ├── storeTypographyTokens.ts
│   └── storeSpacingTokens.ts
├── stores/store/              # Zustand stores
│   ├── cart.ts                # Cart state (persist)
│   ├── wishlist.ts            # Wishlist state (persist)
│   ├── customer.ts            # Customer auth state (persist)
│   ├── ui.ts                  # UI state (no persist)
│   ├── recentlyViewed.ts      # Recently viewed products (persist)
│   └── comparison.ts          # Product comparison (persist)
├── styles/store.css           # Store CSS (custom props, dark theme)
└── types/store/               # Storefront type definitions
    ├── product.ts             # StoreProduct, variants, filters
    ├── category.ts            # StoreCategory, tree, breadcrumbs
    ├── cart.ts                # StoreCartItem, StoreCart
    ├── customer.ts            # StoreCustomer, addresses, provinces
    ├── order.ts               # StoreOrder, status, payment
    ├── checkout.ts            # Checkout session, steps, validation
    ├── common.ts              # Shared types (pagination, loading)
    └── api.ts                 # API response types, type guards
```

## Configuration

### Store Config (`lib/store/config.ts`)
Central configuration including store info, API endpoints, currency (LKR/₨), locale (en-LK), and feature flags.

### Shipping (`config/shipping.config.ts`)
5 shipping zones (Colombo Metro → Remote Areas), 3 methods (Standard/Express/Same-Day), free shipping over ₨5,000, COD ₨100 surcharge.

### Payment (`config/payment.config.ts`)
4 methods: Cash on Delivery (max ₨50,000), PayHere (local), Bank Transfer (2 banks), Stripe (international, disabled).

## API Client

Located in `lib/api/store/`, uses a separate Axios instance from the ERP dashboard.

- **Base URL**: `/api/v1/store`
- **Auth**: JWT token with refresh queue for concurrent requests
- **Error handling**: Exponential backoff retry (max 3 retries, 1s base)
- **Modules**: products, categories, cart, checkout, customer, orders, reviews, wishlist, search

## State Management (Zustand)

All stores use the `createStore()` factory from `stores/utils.ts` which provides DevTools → Persist → Immer middleware stack.

| Store | Persist Key | Purpose |
|---|---|---|
| cart | `lcc-store-cart` | Cart items, 8% VAT calculation |
| wishlist | `lcc-store-wishlist` | Wishlist toggle |
| customer | `lcc-store-customer` | Auth state, login/logout |
| ui | (none) | Mobile menu, cart drawer, search |
| recentlyViewed | `lcc-recently-viewed` | FIFO queue, max 10, 30-day prune |
| comparison | `lcc-product-comparison` | Max 4 items, same-category constraint |

## Sri Lankan Localization

| Feature | Value |
|---|---|
| Currency | LKR (₨), 2 decimal places |
| Locale | en-LK |
| Timezone | Asia/Colombo |
| Phone | +94 format, validated |
| Provinces | 9 (Western, Central, Southern, etc.) |
| Postal | 5-digit codes |
| Tax | 8% VAT |

## Common Import Patterns

```typescript
// Configuration
import { storeInfo, formatCurrency } from '@/lib/store';

// Utilities
import { displayPrice, getProductUrl, isInStock } from '@/lib/store/utils';

// Types
import { StoreProduct, StoreCategory, StoreOrder } from '@/types/store';

// API
import { getProducts, getCategories } from '@/lib/api/store';

// Stores
import { useCartStore } from '@/stores/store/cart';
import { useWishlistStore } from '@/stores/store/wishlist';

// Hooks
import { useStoreProducts, useStoreCategories } from '@/hooks/queries';
```
