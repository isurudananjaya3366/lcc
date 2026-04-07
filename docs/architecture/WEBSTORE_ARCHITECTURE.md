# LankaCommerce Cloud — Webstore Architecture

> **Document Type:** Architecture Overview  
> **Phase:** 08 — Webstore & E-Commerce Platform  
> **Status:** Planning (0% implemented)  
> **Total SubPhases:** 14 | **Total Tasks:** ~1,316  
> **Last Updated:** Current Session

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Frontend Architecture](#4-frontend-architecture)
5. [Route & Page Structure](#5-route--page-structure)
6. [Component Architecture](#6-component-architecture)
7. [State Management](#7-state-management)
8. [Theme & Customization Engine](#8-theme--customization-engine)
9. [Product Catalog System](#9-product-catalog-system)
10. [Shopping Cart Architecture](#10-shopping-cart-architecture)
11. [Checkout Flow](#11-checkout-flow)
12. [Customer Authentication & Portal](#12-customer-authentication--portal)
13. [Backend API Integration](#13-backend-api-integration)
14. [Sri Lanka Localization](#14-sri-lanka-localization)
15. [SEO Implementation](#15-seo-implementation)
16. [Performance Optimization](#16-performance-optimization)
17. [CMS & Static Pages](#17-cms--static-pages)
18. [Marketing Features](#18-marketing-features)
19. [Template System Analysis](#19-template-system-analysis)
20. [Plugin & Extensibility Analysis](#20-plugin--extensibility-analysis)
21. [Pre-Built Template Strategy](#21-pre-built-template-strategy)
22. [Additional Architecture Details](#22-additional-architecture-details)
23. [SubPhase Dependencies](#23-subphase-dependencies)
24. [Task Breakdown Summary](#24-task-breakdown-summary)
25. [Key File Paths Reference](#25-key-file-paths-reference)

---

## 1. Executive Summary

The LankaCommerce Cloud Webstore is a **customer-facing e-commerce storefront** that integrates with the ERP backend built in Phases 01–07. It is optimized for **Sri Lankan shoppers** with local payment gateways (PayHere, KOKO, MintPay), cash on delivery, bank transfers, WhatsApp-first communication, and the province/district/city address system (no zip codes).

The webstore lives within the **same Next.js application** as the ERP dashboard, separated by **Next.js Route Groups**. It features a **per-tenant theme customization engine**, allowing each tenant to customize colors, fonts, logos, and homepage layout through a drag-and-drop builder with live preview.

### Key Capabilities

| Capability                  | Description                                                |
| --------------------------- | ---------------------------------------------------------- |
| **Multi-Tenant Storefront** | Each tenant gets their own branded store with custom theme |
| **Product Catalog**         | Category/collection browsing, filtering, sorting, search   |
| **Smart Search**            | Autocomplete, suggestions, recent searches, typo tolerance |
| **Shopping Cart**           | Persistent cart with stock validation, coupon support      |
| **5-Step Checkout**         | Sri Lanka-optimized with local payment & shipping options  |
| **Customer Portal**         | Orders, addresses, wishlist, reviews, settings             |
| **Theme Engine**            | Visual customization with drag-and-drop homepage builder   |
| **CMS**                     | Static pages, blog, rich text editor                       |
| **SEO**                     | Structured data, dynamic sitemap, OpenGraph, meta tags     |
| **Marketing**               | Coupons, flash sales, WhatsApp widget, newsletters         |

---

## 2. System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        NEXT.JS APPLICATION                             │
│                                                                         │
│  ┌──────────────────────┐      ┌──────────────────────────────────┐    │
│  │   (dashboard)/       │      │   (storefront)/                  │    │
│  │   ERP Admin Panel    │      │   Customer-Facing Webstore       │    │
│  │                      │      │                                  │    │
│  │  • Inventory Mgmt    │      │  • Product Catalog               │    │
│  │  • Order Processing  │      │  • Shopping Cart                 │    │
│  │  • Customer CRM      │      │  • Checkout Flow                 │    │
│  │  • Reports           │      │  • Customer Portal               │    │
│  │  • Settings          │      │  • Theme Customization           │    │
│  └──────────┬───────────┘      └──────────────┬───────────────────┘    │
│             │                                  │                        │
│  ┌──────────┴──────────────────────────────────┴───────────────────┐   │
│  │                    SHARED LAYER                                  │   │
│  │  • components/ui/        (Base UI components)                   │   │
│  │  • components/shared/    (Cross-cutting components)             │   │
│  │  • lib/                  (Utilities, API clients)               │   │
│  │  • types/                (Shared TypeScript types)              │   │
│  └─────────────────────────────┬───────────────────────────────────┘   │
│                                │                                        │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │ REST API (JWT Auth)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     DJANGO BACKEND (Multi-Tenant)                       │
│                                                                         │
│  ┌───────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐ │
│  │apps.users │ │apps.orders│ │apps.prod │ │apps.web  │ │apps.tenants│ │
│  │           │ │           │ │ucts      │ │store     │ │           │  │
│  └───────────┘ └───────────┘ └──────────┘ └──────────┘ └───────────┘  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  RBAC · Middleware · Multi-Tenancy · Caching · Celery Tasks    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                                   │
│                                                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐   │
│  │ PayHere │ │  KOKO   │ │MintPay  │ │Koombiyo │ │   WhatsApp   │   │
│  │ Gateway │ │  BNPL   │ │  BNPL   │ │Shipping │ │  Business API│   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────────┘   │
│  ┌─────────┐ ┌─────────┐                                             │
│  │  Domex  │ │  Redis  │                                             │
│  │Shipping │ │  Cache  │                                             │
│  └─────────┘ └─────────┘                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

### Deployment Model

The webstore uses **Route Groups** within the same Next.js application — not a separate app:

```
frontend/app/
├── (dashboard)/        ← ERP Dashboard (admin users)
├── (storefront)/       ← Customer Webstore (shoppers)
├── layout.tsx          ← Root layout (shared)
├── page.tsx            ← Landing/redirect page
└── globals.css         ← Global styles
```

This means:

- **Single deployment** — one Next.js build serves both ERP and webstore
- **Shared codebase** — common UI components, utilities, and types
- **Separate layouts** — each route group has its own `layout.tsx`
- **Independent navigation** — dashboard uses sidebar, webstore uses header/footer
- **Tenant isolation** — subdomain or domain-based tenant routing at the middleware level

---

## 3. Technology Stack

```
┌──────────────────────────────────────────────────────────────┐
│                     FRONTEND STACK                            │
├──────────────┬───────────────────────────────────────────────┤
│ Framework    │ Next.js 14+ (App Router, Server Components)   │
│ Language     │ TypeScript (strict mode)                       │
│ Styling      │ Tailwind CSS + CSS Variables (theme engine)   │
│ Client State │ Zustand (cart, wishlist, auth, UI, checkout)  │
│ Server State │ TanStack Query (data fetching, caching)       │
│ Forms        │ React Hook Form + Zod validation              │
│ Icons        │ Lucide React (tree-shakeable)                 │
│ Animation    │ Framer Motion                                 │
│ Rich Text    │ Tiptap or Slate.js (CMS pages)               │
│ Images       │ Next.js Image (WebP/AVIF, lazy loading)       │
│ Fonts        │ next/font + Google Fonts (dynamic per theme)  │
├──────────────┼───────────────────────────────────────────────┤
│              │             BACKEND STACK                      │
├──────────────┼───────────────────────────────────────────────┤
│ Framework    │ Django + Django REST Framework                 │
│ Database     │ PostgreSQL (multi-tenant schema)               │
│ Auth         │ JWT (access + refresh, httpOnly cookies)       │
│ Cache        │ Redis                                         │
│ Task Queue   │ Celery                                        │
│ API Client   │ Axios (frontend) with interceptors            │
└──────────────┴───────────────────────────────────────────────┘
```

---

## 4. Frontend Architecture

### Directory Structure

```
frontend/
├── app/
│   ├── (dashboard)/                 # ERP Dashboard routes
│   └── (storefront)/                # Webstore routes
│       ├── layout.tsx               # Store layout wrapper
│       ├── page.tsx                 # Homepage
│       ├── loading.tsx              # Global loading state
│       ├── error.tsx                # Error boundary
│       ├── not-found.tsx            # 404 page
│       ├── products/                # Product pages
│       ├── search/                  # Search results
│       ├── cart/                    # Cart page
│       ├── checkout/                # 5-step checkout
│       └── account/                 # Customer portal
│
├── components/
│   ├── ui/                          # Base UI (shared)
│   ├── modules/                     # ERP-specific modules
│   ├── storefront/                  # Webstore components
│   │   ├── layout/                  # Header, Footer, MegaMenu, MobileNav
│   │   ├── product/                 # Gallery, ProductInfo, Variants
│   │   ├── catalog/                 # ProductGrid, Filters, Pagination
│   │   ├── search/                  # SearchInput, Autocomplete
│   │   ├── cart/                    # MiniCart, CartPage, CartItem
│   │   ├── checkout/                # CheckoutLayout, Steps, OrderSidebar
│   │   ├── auth/                    # Login, Register, ForgotPassword
│   │   ├── portal/                  # Dashboard, Orders, Addresses
│   │   └── theme/                   # ThemeProvider, ColorPicker, Preview
│   └── shared/                      # Shared between ERP & Store
│
├── stores/storefront/               # Zustand stores
│   ├── cartStore.ts
│   ├── wishlistStore.ts
│   ├── authStore.ts
│   ├── uiStore.ts
│   ├── checkoutStore.ts
│   ├── themeStore.ts
│   ├── couponStore.ts
│   └── flashSaleStore.ts
│
├── services/storefront/             # API service layer
│   ├── cart/
│   ├── checkout/
│   ├── auth/
│   ├── portal/
│   ├── search/
│   ├── product/
│   └── themeService.ts
│
├── hooks/storefront/                # Custom React hooks
│   ├── useCart.ts
│   ├── useWishlist.ts
│   ├── useAuth.ts
│   ├── useTheme.ts
│   ├── useDebounce.ts              # 300ms for search
│   ├── useRecentSearches.ts
│   ├── useProducts.ts
│   └── useCountdown.ts             # Flash sales
│
├── types/storefront/                # TypeScript types
│   ├── product.ts
│   ├── cart.types.ts
│   ├── customer.ts
│   ├── order.ts
│   ├── theme.types.ts
│   └── seo/
│
├── data/srilanka/                   # Sri Lanka reference data
│   ├── provinces.ts
│   ├── districts.ts
│   └── cities.ts
│
├── lib/store/                       # Store utilities
│   ├── config.ts
│   ├── routes.ts
│   └── utils.ts
│
└── styles/theme/                    # Theme system
    ├── variables.css
    └── defaults.ts
```

### Data Flow Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        DATA FLOW                                  │
│                                                                   │
│  ┌─────────────────┐    ┌──────────────────┐                     │
│  │ Server Components│───►│ Initial SSR/ISR  │                     │
│  │ (Products, Pages)│    │ Data Fetching    │                     │
│  └─────────────────┘    └────────┬─────────┘                     │
│                                  │                                │
│                                  ▼                                │
│  ┌─────────────────┐    ┌──────────────────┐    ┌──────────┐    │
│  │  TanStack Query  │───►│ Client-Side Data │◄───│ REST API │    │
│  │  (Cache, Refetch) │    │ Fetching/Caching │    │ (Django) │    │
│  └─────────────────┘    └────────┬─────────┘    └──────────┘    │
│                                  │                                │
│                                  ▼                                │
│  ┌─────────────────┐    ┌──────────────────┐                     │
│  │  Zustand Stores  │───►│ Client State     │                     │
│  │  (Cart, Auth, UI)│    │ (In-Memory)      │                     │
│  └────────┬────────┘    └──────────────────┘                     │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐    ┌──────────────────┐                     │
│  │  localStorage    │───►│ Persistence      │                     │
│  │  (Cart, Searches)│    │ Layer            │                     │
│  └─────────────────┘    └──────────────────┘                     │
│                                                                   │
│  ┌─────────────────┐    ┌──────────────────┐                     │
│  │  URL Params      │───►│ Filter/Sort/     │                     │
│  │  (Shareable)     │    │ Search State     │                     │
│  └─────────────────┘    └──────────────────┘                     │
└───────────────────────────────────────────────────────────────────┘
```

---

## 5. Route & Page Structure

### Store Routes

```
(storefront)/
│
├── page.tsx                              # Homepage
│
├── products/
│   ├── page.tsx                          # All products listing
│   ├── category/[slug]/page.tsx          # Category products
│   ├── collection/[slug]/page.tsx        # Collection products
│   └── [slug]/page.tsx                   # Product detail page
│
├── search/
│   └── page.tsx                          # Search results
│
├── cart/
│   └── page.tsx                          # Full cart page
│
├── checkout/
│   ├── information/page.tsx              # Step 1: Contact info
│   ├── shipping/page.tsx                 # Step 2: Address & method
│   ├── payment/page.tsx                  # Step 3: Payment method
│   ├── review/page.tsx                   # Step 4: Order review
│   └── confirmation/page.tsx             # Step 5: Success page
│
├── account/
│   ├── login/page.tsx                    # Login
│   ├── register/page.tsx                 # Registration
│   ├── forgot-password/page.tsx          # Password reset request
│   ├── reset-password/page.tsx           # Password reset form
│   ├── dashboard/page.tsx                # Account overview
│   ├── orders/page.tsx                   # Order history
│   ├── orders/[id]/page.tsx              # Order detail
│   ├── addresses/page.tsx                # Address book
│   ├── wishlist/page.tsx                 # Wishlist
│   ├── reviews/page.tsx                  # My reviews
│   └── settings/page.tsx                 # Account settings
│
├── pages/[slug]/page.tsx                 # CMS pages (About, Contact, etc.)
├── blog/page.tsx                         # Blog listing
└── blog/[slug]/page.tsx                  # Blog post detail
```

---

## 6. Component Architecture

### Storefront Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ANNOUNCEMENT BAR (configurable, dismissible)                    │
│  "Free shipping on orders over ₨5,000"                         │
├─────────────────────────────────────────────────────────────────┤
│ HEADER                                                          │
│ [Logo]  [Categories ▼]  [🔍 Search...]  [👤 Account] [🛒 (3)] │
│         └─ MegaMenu                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                       MAIN CONTENT                              │
│                   (Page-specific)                                │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ FOOTER                                                          │
│ About | Contact | FAQ | Terms | Privacy                         │
│ Newsletter Signup  |  Social Links                              │
│ © 2026 Store Name. All rights reserved.                         │
├─────────────────────────────────────────────────────────────────┤
│                                         [💬 WhatsApp Chat]      │
└─────────────────────────────────────────────────────────────────┘
```

### Component Tree

```
<StoreLayout>
├── <AnnouncementBar />
├── <Header>
│   ├── <Logo />
│   ├── <MegaMenu />
│   ├── <SearchInput>
│   │   └── <Autocomplete />
│   ├── <AccountButton />
│   └── <CartIcon>
│       └── <MiniCart />           ← Dropdown
├── <MobileNav>                    ← Drawer (mobile only)
│   ├── <MobileSearch />
│   ├── <MobileCategoryNav />
│   └── <MobileAccountLinks />
│
├── {children}                     ← Page content
│
├── <Footer>
│   ├── <FooterLinks />
│   ├── <NewsletterForm />
│   └── <SocialLinks />
│
└── <FloatingElements>
    └── <WhatsAppWidget />         ← Floating button
```

### Product Card Component

```
┌─────────────────────────┐
│ ┌─────────────────────┐ │
│ │                     │ │  ← Image with hover effect
│ │    Product Image    │ │  ← Lazy loaded
│ │                     │ │
│ │  [SALE -20%]   [♡] │ │  ← Badge + Wishlist
│ └─────────────────────┘ │
│                         │
│ Electronics > Phones     │  ← Category link
│ iPhone 15 Pro Max       │  ← Product name
│ ⭐⭐⭐⭐⭐ (42)             │  ← Rating
│                         │
│ ₨̶ ̶2̶4̶9̶,̶0̶0̶0̶              │  ← Original (strikethrough)
│ ₨199,000                │  ← Sale price
│                         │
│ [   Add to Cart    ]    │  ← Quick add CTA
└─────────────────────────┘
```

### Product Detail Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Breadcrumb: Home > Electronics > Phones > iPhone 15 Pro Max     │
├─────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────┐  PRODUCT INFO                         │
│ │                       │                                       │
│ │   ┌───────────────┐   │  iPhone 15 Pro Max                    │
│ │   │  Main Image   │   │  SKU: IPH-15PM-256                   │
│ │   │  (with zoom)  │   │  ⭐⭐⭐⭐⭐ (42 reviews)                │
│ │   └───────────────┘   │                                       │
│ │                       │  ₨̶ ̶2̶4̶9̶,̶0̶0̶0̶  ₨199,000  (20% off)    │
│ │  [1] [2] [3] [4]     │  Inclusive of all taxes               │
│ │  ← Thumbnails →      │                                       │
│ └───────────────────────┘  Storage: [128GB] [256GB] [512GB]     │
│                            Color:   [⚫] [⚪] [🔵] [🟤]        │
│                                                                 │
│                            Quantity: [−] 1 [+]                  │
│                            ✅ In Stock (Only 5 left!)           │
│                            🚚 Est. delivery: 3-5 business days  │
│                                                                 │
│                            [    Add to Cart    ]                │
│                            [     Buy Now       ]                │
│                            [♡ Add to Wishlist]                  │
│                                                                 │
│                            Share: [WhatsApp] [Facebook]         │
├─────────────────────────────────────────────────────────────────┤
│ [Description] [Specifications] [Reviews (42)]    ← Tabs        │
│━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│ Tab content area...                                             │
├─────────────────────────────────────────────────────────────────┤
│ RELATED PRODUCTS                                                │
│ [Card] [Card] [Card] [Card]   ← Horizontal scroll              │
├─────────────────────────────────────────────────────────────────┤
│ RECENTLY VIEWED                                                 │
│ [Card] [Card] [Card] [Card]   ← From localStorage              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. State Management

### Zustand Store Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ZUSTAND STORES                            │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  cartStore    │  │ wishlistStore│  │  authStore    │     │
│  │              │  │              │  │              │      │
│  │ items[]      │  │ items[]      │  │ user         │      │
│  │ addItem()    │  │ add()        │  │ isAuthenticated│    │
│  │ removeItem() │  │ remove()     │  │ login()      │      │
│  │ updateQty()  │  │ toggle()     │  │ logout()     │      │
│  │ clearCart()  │  │              │  │ setUser()    │      │
│  │ cartTotal    │  └──────────────┘  └──────────────┘      │
│  │ itemCount    │                                           │
│  └──────┬───────┘  ┌──────────────┐  ┌──────────────┐     │
│         │          │  uiStore     │  │checkoutStore │      │
│         │          │              │  │              │      │
│         ▼          │ mobileMenu   │  │ step (1-5)   │      │
│  ┌──────────────┐  │ overlays     │  │ contact      │      │
│  │ localStorage │  │ toasts       │  │ shipping     │      │
│  │ persistence  │  └──────────────┘  │ payment      │      │
│  └──────────────┘                    │ review       │      │
│                    ┌──────────────┐  └──────────────┘      │
│                    │ themeStore   │  ┌──────────────┐      │
│                    │              │  │ couponStore   │      │
│                    │ colors       │  │              │      │
│                    │ fonts        │  │ code          │      │
│                    │ logo         │  │ discount      │      │
│                    │ homepage     │  │ validate()    │      │
│                    └──────────────┘  └──────────────┘      │
│                                      ┌──────────────┐      │
│                                      │flashSaleStore│      │
│                                      │              │      │
│                                      │ activeSales  │      │
│                                      │ countdown    │      │
│                                      └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Cart Persistence Flow

```
                    ┌─────────────┐
                    │  User adds  │
                    │  item to    │
                    │  cart       │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
            ┌───── │ Logged in?  │ ─────┐
            │ No   └─────────────┘  Yes │
            ▼                           ▼
    ┌───────────────┐          ┌───────────────┐
    │ Save to       │          │ Save to       │
    │ localStorage  │          │ localStorage  │
    │ (guest cart)  │          │ + Sync to API │
    └───────┬───────┘          └───────────────┘
            │
            │  User logs in later
            ▼
    ┌───────────────┐
    │ Merge guest   │
    │ cart with     │
    │ API cart      │
    └───────────────┘
```

---

## 8. Theme & Customization Engine

> **SubPhase 10** — 92 tasks | Per-tenant visual customization

### Theme Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    THEME ENGINE                                  │
│                                                                 │
│  ┌──────────────┐    ┌───────────────────┐                     │
│  │  Tenant DB   │───►│  Theme Settings   │                     │
│  │  Config      │    │  (JSON blob)      │                     │
│  └──────────────┘    └────────┬──────────┘                     │
│                               │                                 │
│                               ▼                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                  ThemeProvider (React Context)          │    │
│  │                                                        │    │
│  │  ┌──────────────────┐  ┌──────────────────────────┐   │    │
│  │  │ CSSVariables     │  │ GoogleFontsLoader        │   │    │
│  │  │ Injector         │  │ (dynamic font loading)   │   │    │
│  │  │                  │  │                          │   │    │
│  │  │ --color-primary  │  │ heading: "Inter"         │   │    │
│  │  │ --color-secondary│  │ body: "Open Sans"        │   │    │
│  │  │ --color-accent   │  │ fallback stacks          │   │    │
│  │  │ --color-bg       │  └──────────────────────────┘   │    │
│  │  │ --color-text     │                                  │    │
│  │  │ --font-heading   │  ┌──────────────────────────┐   │    │
│  │  │ --font-body      │  │ HomepageBuilder          │   │    │
│  │  └──────────────────┘  │ (drag-and-drop sections) │   │    │
│  │                        │                          │   │    │
│  │                        │ • Hero Banner            │   │    │
│  │                        │ • Featured Products      │   │    │
│  │                        │ • Categories Grid        │   │    │
│  │                        │ • Testimonials           │   │    │
│  │                        │ • Newsletter Signup      │   │    │
│  │                        └──────────────────────────┘   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                  Admin Preview Panel                    │    │
│  │                                                        │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │    │
│  │  │ Desktop  │  │  Mobile  │  │ Draft / Publish  │    │    │
│  │  │ Preview  │  │ Preview  │  │ Workflow         │    │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘    │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Theme Settings JSON Structure

```json
{
  "logo": {
    "desktop": "/uploads/logo.png",
    "mobile": "/uploads/logo-mobile.png",
    "favicon": "/uploads/favicon.ico"
  },
  "colors": {
    "primary": "#2563eb",
    "secondary": "#64748b",
    "accent": "#f59e0b",
    "background": "#ffffff",
    "text": "#1f2937"
  },
  "fonts": {
    "heading": "Inter",
    "body": "Open Sans"
  },
  "homepage": {
    "sections": [
      { "type": "hero", "enabled": true, "order": 1 },
      { "type": "featured_products", "enabled": true, "order": 2 },
      { "type": "categories", "enabled": true, "order": 3 },
      { "type": "testimonials", "enabled": false, "order": 4 },
      { "type": "newsletter", "enabled": true, "order": 5 }
    ],
    "hero": {
      "image": "/uploads/hero-banner.jpg",
      "title": "Welcome to Our Store",
      "subtitle": "Best deals on electronics",
      "ctaText": "Shop Now",
      "ctaLink": "/products"
    }
  },
  "announcement": {
    "enabled": true,
    "text": "Free shipping on orders over ₨5,000",
    "backgroundColor": "#2563eb",
    "textColor": "#ffffff"
  }
}
```

### Customization Capabilities

| Feature           | What's Customizable                                                  |
| ----------------- | -------------------------------------------------------------------- |
| **Colors**        | Primary, secondary, accent, background, text + auto-generated shades |
| **Fonts**         | Heading font + body font from Google Fonts library                   |
| **Logo**          | Desktop logo, mobile logo, favicon with image cropper                |
| **Homepage**      | Drag-and-drop section ordering, enable/disable sections              |
| **Hero Banner**   | Image, title, subtitle, CTA button text + link                       |
| **Announcement**  | Text, colors, dismissible toggle                                     |
| **Footer**        | Links, social media, newsletter section                              |
| **Live Preview**  | Desktop and mobile viewport preview in iframe                        |
| **Draft/Publish** | Save changes as draft, preview before publishing live                |

---

## 9. Product Catalog System

> **SubPhases 03-04** — 190 tasks total

### Catalog Page Types

```
/products                          → All products (default grid)
/products/category/[slug]          → Category page (with banner)
/products/collection/[slug]        → Collection page (with story)
/products/[slug]                   → Product detail page
```

### Filter Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCT CATALOG PAGE                          │
│                                                                 │
│ ┌───────────────┐  ┌───────────────────────────────────────┐   │
│ │ FILTER SIDEBAR│  │  TOOLBAR                               │   │
│ │               │  │  [Grid/List] Sort: [Newest ▼] (24 items)│   │
│ │ Categories    │  ├───────────────────────────────────────┤   │
│ │ □ Electronics │  │                                       │   │
│ │ □ Clothing    │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │   │
│ │ □ Home        │  │  │Card │ │Card │ │Card │ │Card │   │   │
│ │               │  │  └─────┘ └─────┘ └─────┘ └─────┘   │   │
│ │ Price Range   │  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │   │
│ │ ₨0 ━━●━━━ ₨50k│  │  │Card │ │Card │ │Card │ │Card │   │   │
│ │               │  │  └─────┘ └─────┘ └─────┘ └─────┘   │   │
│ │ Color         │  │                                       │   │
│ │ 🔴 🔵 ⚫ ⚪  │  │  [1] [2] [3] ... [Load More]        │   │
│ │               │  │                                       │   │
│ │ Size          │  └───────────────────────────────────────┘   │
│ │ □ S □ M □ L  │                                               │
│ │               │                                               │
│ │ □ In Stock    │  Active Filters: [Electronics ×] [₨0-₨20k ×]│
│ │ □ On Sale     │                                               │
│ │               │                                               │
│ │ [Apply] [Clear]│                                              │
│ └───────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Sort Options

| Option             | API Parameter  |
| ------------------ | -------------- |
| Newest First       | `-created_at`  |
| Price: Low to High | `price`        |
| Price: High to Low | `-price`       |
| Most Popular       | `-sales_count` |
| Highest Rated      | `-avg_rating`  |

### Search Architecture

```
┌──────────────────────────────────────────┐
│  [🔍 Search products...          ]       │
│  ┌────────────────────────────────────┐  │
│  │ SUGGESTIONS                        │  │
│  │                                    │  │
│  │ Products:                          │  │
│  │  📱 iPhone 15 Pro Max             │  │
│  │  📱 iPhone 15                      │  │
│  │                                    │  │
│  │ Categories:                        │  │
│  │  📂 Electronics > Phones           │  │
│  │                                    │  │
│  │ Recent Searches:                   │  │
│  │  🕐 samsung galaxy                │  │
│  │  🕐 wireless earbuds              │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘

Features:
• 300ms debounce on keystroke
• Autocomplete with product + category suggestions
• Recent searches from localStorage
• "Did you mean?" for typos
• Sinhala-glish support (future: Phase 10)
```

---

## 10. Shopping Cart Architecture

> **SubPhase 06** — 96 tasks

### Cart Components

```
┌─── MINI CART (Header Dropdown) ────────────┐
│                                            │
│  🛒 Your Cart (3 items)                    │
│  ┌──────────────────────────────────────┐  │
│  │ [img] Product Name          ₨1,999  │  │
│  │       Size: M, Color: Blue    [×]   │  │
│  │ [img] Product Name          ₨2,499  │  │
│  │       Qty: 2                  [×]   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  Subtotal:                 ₨6,997          │
│                                            │
│  [   View Cart   ] [   Checkout   ]        │
└────────────────────────────────────────────┘


┌─── CART PAGE (/cart) ──────────────────────────────────────────┐
│                                                                │
│  ┌──────────────────────────────────┐  ┌──────────────────┐   │
│  │ CART ITEMS                        │  │ ORDER SUMMARY     │   │
│  │                                  │  │                  │   │
│  │ ┌──────────────────────────────┐ │  │ Subtotal: ₨6,997 │   │
│  │ │[img] Product Name           │ │  │ Discount: -₨500  │   │
│  │ │      Size: M | Color: Blue  │ │  │ Shipping: TBD    │   │
│  │ │      ₨1,999 × [−] 1 [+]    │ │  │ ─────────────    │   │
│  │ │      = ₨1,999        [🗑️]   │ │  │ Total:   ₨6,497 │   │
│  │ │      ⚠️ Only 3 left!        │ │  │                  │   │
│  │ └──────────────────────────────┘ │  │ Coupon: [____]   │   │
│  │                                  │  │ [Apply]          │   │
│  │ ┌──────────────────────────────┐ │  │                  │   │
│  │ │[img] Product Name           │ │  │ [Proceed to      │   │
│  │ │      ₨2,499 × [−] 2 [+]    │ │  │  Checkout   ]    │   │
│  │ │      = ₨4,998        [🗑️]   │ │  │                  │   │
│  │ └──────────────────────────────┘ │  │ 🔒 Secure        │   │
│  │                                  │  │    Checkout      │   │
│  │ [← Continue Shopping]            │  └──────────────────┘   │
│  └──────────────────────────────────┘                          │
└────────────────────────────────────────────────────────────────┘
```

### Cart Store (Zustand) Actions & Selectors

| Action/Selector                  | Description                        |
| -------------------------------- | ---------------------------------- |
| `addItem(product, variant, qty)` | Add item with variant key          |
| `removeItem(itemKey)`            | Remove item from cart              |
| `updateQuantity(itemKey, qty)`   | Update quantity (min 1, max stock) |
| `clearCart()`                    | Remove all items                   |
| `cartTotal`                      | Computed total in LKR              |
| `cartItemCount`                  | Total items count                  |
| `cartSubtotal`                   | Subtotal before discounts          |

---

## 11. Checkout Flow

> **SubPhase 07** — 98 tasks | 5-step wizard with URL-based routing

### Checkout Steps Diagram

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────────┐
│  STEP  │───►│  STEP  │───►│  STEP  │───►│  STEP  │───►│   STEP     │
│   1    │    │   2    │    │   3    │    │   4    │    │    5       │
│        │    │        │    │        │    │        │    │            │
│ INFO   │    │SHIPPING│    │PAYMENT │    │ REVIEW │    │CONFIRMATION│
└────┬───┘    └────┬───┘    └────┬───┘    └────┬───┘    └────────────┘
     │             │             │             │
     ▼             ▼             ▼             ▼
 ┌────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
 │Email   │  │Province  │  │PayHere   │  │Items     │
 │Phone   │  │District  │  │Card      │  │Address   │
 │(+94)   │  │City      │  │Bank Xfer │  │Payment   │
 │Name    │  │Address   │  │COD       │  │Total     │
 │WhatsApp│  │Landmark  │  │KOKO      │  │          │
 │opt-in  │  │Method    │  │MintPay   │  │[Place    │
 │        │  │(Std/Exp) │  │          │  │ Order]   │
 └────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Step Details

#### Step 1: Information (`/checkout/information`)

| Field            | Details                              |
| ---------------- | ------------------------------------ |
| Email            | Standard email validation            |
| Phone            | Sri Lanka format (+94 XX XXX XXXX)   |
| WhatsApp Updates | Checkbox for order notifications     |
| First Name       | Required                             |
| Last Name        | Required                             |
| Login Prompt     | "Already have an account? Log in"    |
| Guest Checkout   | Fully supported without registration |

#### Step 2: Shipping (`/checkout/shipping`)

| Field           | Details                                              |
| --------------- | ---------------------------------------------------- |
| Province        | Dropdown (9 provinces)                               |
| District        | Filtered by province                                 |
| City            | Filtered by district                                 |
| Address Line 1  | Street address                                       |
| Address Line 2  | Optional                                             |
| Landmark        | Optional (helpful for delivery)                      |
| Saved Addresses | Quick select for logged-in users                     |
| Shipping Method | Standard (₨350, 3-5 days) / Express (₨650, 1-2 days) |

**Note:** Sri Lanka does NOT use zip/postal codes.

#### Step 3: Payment (`/checkout/payment`)

| Method            | Type        | Details                             |
| ----------------- | ----------- | ----------------------------------- |
| PayHere           | Gateway     | Redirect to PayHere payment page    |
| Credit/Debit Card | Via gateway | Visa, Mastercard, Amex              |
| Bank Transfer     | Manual      | Shows bank details + receipt upload |
| Cash on Delivery  | COD         | With availability conditions        |
| KOKO              | BNPL        | Buy Now, Pay Later (3 installments) |
| MintPay           | BNPL        | Buy Now, Pay Later                  |

#### Step 4: Review (`/checkout/review`)

Summary of all previous steps with edit links. "Place Order" button.

#### Step 5: Confirmation (`/checkout/confirmation`)

Order number, success animation, WhatsApp confirmation, "Continue Shopping" CTA.

### Checkout Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ PROGRESS: [1 ●]───[2 ●]───[3 ○]───[4 ○]───[5 ○]              │
│           Info    Ship    Pay     Review   Done                  │
├─────────────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────┐  ┌────────────────────────┐  │
│ │                               │  │ ORDER SIDEBAR           │  │
│ │  STEP CONTENT                 │  │                        │  │
│ │  (form fields for             │  │ [img] Product ₨1,999  │  │
│ │   current step)               │  │ [img] Product ₨4,998  │  │
│ │                               │  │                        │  │
│ │                               │  │ Subtotal:   ₨6,997    │  │
│ │                               │  │ Shipping:   ₨350      │  │
│ │                               │  │ Discount:   -₨500     │  │
│ │                               │  │ ────────────────       │  │
│ │  [← Back]      [Continue →]  │  │ Total:      ₨6,847    │  │
│ └───────────────────────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Customer Authentication & Portal

> **SubPhases 08-09** — 190 tasks total

### Authentication Flow

```
                    ┌─────────────────┐
                    │  Customer visits │
                    │  /account/login  │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                ▼            │            ▼
        ┌──────────┐        │    ┌──────────────┐
        │  Email   │        │    │  Phone (+94) │
        │  Login   │        │    │  Login       │
        └────┬─────┘        │    └──────┬───────┘
             │              │           │
             └──────┬───────┘           │
                    ▼                   │
            ┌──────────────┐            │
            │  Credentials │◄───────────┘
            │  Verified?   │
            └──────┬───────┘
                   │
           ┌───────┼───────┐
           ▼               ▼
    ┌──────────┐    ┌──────────┐
    │  JWT     │    │  Error   │
    │  Issued  │    │  Message │
    │          │    └──────────┘
    │  Access: │
    │  15 min  │
    │          │
    │  Refresh:│
    │  7 days  │
    │  (30 w/  │
    │  remember│
    │  me)     │
    └────┬─────┘
         │
         ▼
    ┌──────────────┐
    │  Merge guest │
    │  cart with   │
    │  account     │
    └──────────────┘
```

### Customer Portal Structure

```
/account/
├── dashboard       ← Welcome card, stats, recent orders, quick actions
├── orders          ← Order history with status filter
├── orders/[id]     ← Order detail with tracking
├── addresses       ← Address book (Province → District → City)
├── wishlist        ← Saved products
├── reviews         ← My product reviews
└── settings        ← Profile, password, notifications, delete account
```

### Order Tracking States

```
[Placed] ──► [Confirmed] ──► [Shipped] ──► [Out for Delivery] ──► [Delivered]
   ●             ●               ●                ○                    ○

Legend: ● = completed, ○ = pending
```

---

## 13. Backend API Integration

### API Endpoint Groups

```
┌─────────────────────────────────────────────────────────────────┐
│                    STOREFRONT API ENDPOINTS                      │
│                                                                 │
│  Products & Catalog                                             │
│  ├── GET  /api/v1/store/products/          (list, filter, sort) │
│  ├── GET  /api/v1/store/products/{slug}/   (detail)             │
│  ├── GET  /api/v1/store/products/{slug}/related/                │
│  ├── GET  /api/v1/store/categories/        (tree)               │
│  └── GET  /api/v1/store/collections/       (list)               │
│                                                                 │
│  Search                                                         │
│  ├── GET  /api/v1/store/search/?q=         (results)            │
│  └── GET  /api/v1/store/search/suggest/?q= (autocomplete)      │
│                                                                 │
│  Cart                                                           │
│  ├── GET  /api/v1/store/cart/              (get cart)           │
│  ├── POST /api/v1/store/cart/items/        (add item)          │
│  ├── PATCH/api/v1/store/cart/items/{id}/   (update qty)        │
│  ├── DEL  /api/v1/store/cart/items/{id}/   (remove)            │
│  └── POST /api/v1/store/cart/validate/     (stock check)       │
│                                                                 │
│  Checkout & Orders                                              │
│  ├── POST /api/v1/store/checkout/          (place order)       │
│  ├── POST /api/v1/store/coupons/validate/  (validate coupon)   │
│  ├── GET  /api/v1/store/orders/            (order history)     │
│  └── GET  /api/v1/store/orders/{id}/       (order detail)      │
│                                                                 │
│  Customer Auth                                                  │
│  ├── POST /api/v1/store/auth/register/     (signup)            │
│  ├── POST /api/v1/store/auth/login/        (login)             │
│  ├── POST /api/v1/store/auth/refresh/      (token refresh)     │
│  ├── POST /api/v1/store/auth/password-reset/(request reset)    │
│  └── POST /api/v1/store/auth/password-reset/confirm/           │
│                                                                 │
│  Customer Portal                                                │
│  ├── GET  /api/v1/store/profile/           (get profile)       │
│  ├── PATCH/api/v1/store/profile/           (update profile)    │
│  ├── GET  /api/v1/store/addresses/         (list addresses)    │
│  ├── POST /api/v1/store/addresses/         (add address)       │
│  ├── GET  /api/v1/store/wishlist/          (list wishlist)     │
│  ├── POST /api/v1/store/wishlist/          (add to wishlist)   │
│  ├── GET  /api/v1/store/reviews/           (my reviews)        │
│  └── POST /api/v1/store/reviews/           (write review)      │
│                                                                 │
│  Theme & CMS                                                    │
│  ├── GET  /api/v1/store/theme/             (get theme config)  │
│  ├── GET  /api/v1/store/pages/{slug}/      (CMS page)         │
│  ├── GET  /api/v1/store/blog/              (blog posts)        │
│  └── GET  /api/v1/store/banners/           (promotional)       │
│                                                                 │
│  Marketing                                                      │
│  ├── GET  /api/v1/store/flash-sales/       (active sales)     │
│  └── POST /api/v1/store/newsletter/        (subscribe)         │
└─────────────────────────────────────────────────────────────────┘
```

### API Client Architecture

```
┌──────────────────┐         ┌──────────────────┐
│  Store API       │ ────►   │  Axios Instance  │
│  Client          │         │  (Separate from  │
│                  │         │   ERP client)    │
│  Base URL:       │         │                  │
│  /api/v1/store/  │         │  Interceptors:   │
│                  │         │  • JWT token     │
│                  │         │  • Auto-refresh  │
│                  │         │  • Error handler │
└──────────────────┘         └──────────────────┘
```

---

## 14. Sri Lanka Localization

### Currency & Locale

```
┌──────────────────────────────────────────┐
│          STORE CONFIGURATION             │
│                                          │
│  currency:      "LKR"                    │
│  currencySymbol: "₨"                     │
│  locale:        "en-LK"                  │
│  timezone:      "Asia/Colombo"           │
│  phoneCode:     "+94"                    │
│  priceFormat:   "₨{amount}"              │
└──────────────────────────────────────────┘
```

### Address System (No Zip Codes)

```
Province (9 total)
    ├── Western Province
    │   ├── Colombo District
    │   │   ├── Colombo 01
    │   │   ├── Colombo 02
    │   │   ├── Dehiwala
    │   │   └── ...
    │   ├── Gampaha District
    │   │   ├── Gampaha
    │   │   ├── Negombo
    │   │   └── ...
    │   └── Kalutara District
    │       └── ...
    ├── Central Province
    │   ├── Kandy District
    │   ├── Matale District
    │   └── Nuwara Eliya District
    ├── Southern Province
    │   └── ...
    └── ... (6 more provinces)

Reference Data Files:
  frontend/data/srilanka/provinces.ts
  frontend/data/srilanka/districts.ts   ← filtered by province
  frontend/data/srilanka/cities.ts      ← filtered by district
```

### Payment Methods

```
┌─────────────────────────────────────────────────────────────────┐
│                    PAYMENT OPTIONS                               │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │    PayHere       │  │  Credit/Debit   │  │ Bank Transfer  │ │
│  │    Gateway       │  │  Card           │  │                │ │
│  │                 │  │                 │  │  Show bank     │ │
│  │  Redirect to    │  │  Visa           │  │  details +     │ │
│  │  PayHere page   │  │  Mastercard     │  │  receipt       │ │
│  │  for payment    │  │  Amex           │  │  upload        │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │    Cash on       │  │    KOKO         │  │   MintPay      │ │
│  │    Delivery      │  │    BNPL         │  │   BNPL         │ │
│  │                 │  │                 │  │                │ │
│  │  Availability   │  │  Buy Now        │  │  Buy Now       │ │
│  │  conditions     │  │  Pay in 3       │  │  Pay Later     │ │
│  │  apply          │  │  installments   │  │                │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
│                                                                 │
│  Note: Full integration in Phase 09. Phase 08 creates stubs.   │
└─────────────────────────────────────────────────────────────────┘
```

### WhatsApp Integration

```
WhatsApp is the PRIMARY communication channel for Sri Lankan customers:

┌─────────────────────────────────────────────────────────┐
│  WHATSAPP TOUCHPOINTS                                    │
│                                                         │
│  • Floating chat widget on all pages                    │
│  • Product inquiry button ("Ask about this product")    │
│  • Cart summary share ("Share cart via WhatsApp")       │
│  • Order confirmation via WhatsApp                      │
│  • Password reset OTP via WhatsApp                      │
│  • Product share button on product detail page          │
│  • Order support link in customer portal                │
│  • Pre-built message templates with context             │
│  • Click-to-chat with +94 phone format                  │
│  • Analytics tracking on WhatsApp interactions          │
└─────────────────────────────────────────────────────────┘
```

### Shipping (Phase 09 Integration)

| Provider | Type              | Coverage                          |
| -------- | ----------------- | --------------------------------- |
| Koombiyo | API Integration   | Island-wide, district-based zones |
| Domex    | API Integration   | Major cities and districts        |
| Standard | 3-5 business days | ₨350                              |
| Express  | 1-2 business days | ₨650                              |

---

## 15. SEO Implementation

> **SubPhase 12** — 92 tasks

### SEO Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       SEO LAYER                                  │
│                                                                 │
│  Meta Tags (Next.js Metadata API)                               │
│  ├── generateMetadata() per page                                │
│  ├── Title template: "Page Title | Store Name"                  │
│  ├── Description: max 160 characters                            │
│  ├── Keywords: product-specific                                 │
│  └── Canonical URLs: pagination & filter aware                  │
│                                                                 │
│  Open Graph                                                     │
│  ├── og:title, og:description, og:image                        │
│  ├── og:type: product / article                                 │
│  ├── og:url, og:site_name, og:locale                           │
│  └── Product-specific: price, availability                      │
│                                                                 │
│  Structured Data (JSON-LD)                                      │
│  ├── Organization                                               │
│  ├── WebSite (with SearchAction)                                │
│  ├── Product (with Offer, AggregateRating)                     │
│  ├── BreadcrumbList                                             │
│  ├── Article (blog posts)                                       │
│  ├── FAQPage                                                    │
│  ├── ContactPage                                                │
│  ├── LocalBusiness                                              │
│  └── CollectionPage                                             │
│                                                                 │
│  Dynamic Sitemap (app/sitemap.ts)                               │
│  ├── Static URLs (home, about, contact)                         │
│  ├── Product URLs (all products with lastmod)                   │
│  ├── Category URLs                                              │
│  ├── Collection URLs                                            │
│  ├── Blog URLs                                                  │
│  ├── CMS page URLs                                              │
│  ├── Separate product sitemap for large catalogs                │
│  └── Image sitemap                                              │
│                                                                 │
│  Robots.txt (app/robots.ts)                                     │
│  ├── Allow: /products, /categories, /blog                      │
│  ├── Disallow: /account, /cart, /checkout                      │
│  └── Sitemap reference                                          │
│                                                                 │
│  SEO Preview Component (Admin)                                  │
│  ├── Google SERP preview                                        │
│  ├── Social share preview                                       │
│  └── Character limit indicators                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 16. Performance Optimization

> **SubPhase 13** — 94 tasks

### Performance Targets

| Metric                         | Target |
| ------------------------------ | ------ |
| Lighthouse Score               | > 90   |
| First Contentful Paint (FCP)   | < 1.5s |
| Largest Contentful Paint (LCP) | < 2.5s |
| Time to Interactive (TTI)      | < 3.5s |
| Cumulative Layout Shift (CLS)  | < 0.1  |

### Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                  PERFORMANCE OPTIMIZATIONS                       │
│                                                                 │
│  IMAGE OPTIMIZATION                                             │
│  ├── Next.js Image component (auto WebP/AVIF)                 │
│  ├── Lazy loading (below-the-fold)                             │
│  ├── Priority loading (above-the-fold hero, product images)    │
│  ├── Blur placeholders during load                             │
│  ├── Responsive srcSet for different viewports                 │
│  └── CDN delivery                                              │
│                                                                 │
│  CODE SPLITTING                                                 │
│  ├── Route-based splitting (automatic in Next.js)              │
│  ├── Dynamic imports (modals, gallery, charts, rich text)      │
│  ├── Bundle analyzer integration                               │
│  ├── Vendor chunking (common dependencies)                     │
│  └── Tree-shaking (Lucide icons, lodash, date-fns)            │
│                                                                 │
│  STATIC GENERATION & ISR                                        │
│  ├── Homepage: Static generation                               │
│  ├── Category pages: Static with ISR revalidation              │
│  ├── Product pages: ISR with on-demand revalidation            │
│  ├── CMS/blog pages: Static on build                           │
│  ├── generateStaticParams for popular products                 │
│  └── Hover prefetch for navigation links                       │
│                                                                 │
│  CACHING                                                        │
│  ├── TanStack Query: staleTime + cacheTime per query           │
│  ├── HTTP Cache-Control headers + ETags                        │
│  ├── CDN edge caching (Vercel/Cloudflare)                      │
│  ├── Long-cache for static assets                              │
│  ├── localStorage for cart, searches, recently viewed          │
│  └── Service worker (offline preparation)                      │
│                                                                 │
│  FONT OPTIMIZATION                                              │
│  ├── next/font (self-hosted, no layout shift)                  │
│  ├── font-display: swap                                        │
│  ├── Latin subset only                                         │
│  ├── Preload critical fonts                                    │
│  └── CSS variable font references                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 17. CMS & Static Pages

> **SubPhase 11** — 94 tasks

### Page Types

| Page               | Route             | Content                                    |
| ------------------ | ----------------- | ------------------------------------------ |
| About Us           | `/pages/about`    | Hero, company story, mission, values, team |
| Contact Us         | `/pages/contact`  | Contact form + WhatsApp link + map         |
| FAQ                | `/pages/faq`      | Accordion with search + categories         |
| Terms & Conditions | `/pages/terms`    | Legal content                              |
| Privacy Policy     | `/pages/privacy`  | Legal content                              |
| Return Policy      | `/pages/returns`  | Process steps with visual flow             |
| Shipping Info      | `/pages/shipping` | Rates table by district                    |
| Blog Listing       | `/blog`           | Grid cards with featured image             |
| Blog Post          | `/blog/[slug]`    | Rich content with share buttons            |
| Custom Pages       | `/pages/[slug]`   | Dynamic CMS-driven pages                   |

### CMS Features

- Rich text editor (Tiptap or Slate.js)
- Content blocks: text, images, videos, quotes, lists, tables
- SEO fields per page (title, description, OG image)
- Draft/Published status workflow
- Dynamic routing via `[slug]` parameter

---

## 18. Marketing Features

> **SubPhase 14** — 96 tasks

### Feature Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MARKETING FEATURES                            │
│                                                                 │
│  COUPONS                                                        │
│  ├── Percentage discount (e.g., 20% off)                       │
│  ├── Fixed amount discount (e.g., ₨500 off)                   │
│  ├── Free shipping                                             │
│  ├── Buy X Get Y                                               │
│  ├── Minimum order value condition                             │
│  ├── Product/category-specific                                 │
│  ├── First order only                                          │
│  ├── Expiry dates + usage limits                               │
│  └── UI: Input + validate, available coupons list              │
│                                                                 │
│  FLASH SALES                                                    │
│  ├── Countdown timer (flip/slide animation)                    │
│  ├── Homepage banner + dedicated section                       │
│  ├── Special product cards with stock counter                  │
│  ├── Dedicated sale page with category filter                  │
│  ├── End notification                                          │
│  └── Festival-based (Vesak, Avurudu, Christmas)                │
│                                                                 │
│  PROMOTIONAL BANNERS                                            │
│  ├── Banner carousel on homepage                               │
│  ├── CTA buttons with configurable links                       │
│  └── Dismissible announcement bar                              │
│                                                                 │
│  POPUPS                                                         │
│  ├── Entry popup (first visit)                                 │
│  ├── Exit intent popup                                         │
│  ├── Scroll-triggered popup                                    │
│  └── Frequency control (once per session)                      │
│                                                                 │
│  NEWSLETTER                                                     │
│  ├── Footer subscription form                                  │
│  └── Popup subscription variant                                │
│                                                                 │
│  SOCIAL SHARING                                                 │
│  └── Share buttons on products and blog posts                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 19. Template System Analysis

> **Question: Does the webstore have a template system?**
> **Answer: NO — but it CAN and SHOULD.**

### Current State: Theme Customizer (Not Templates)

The current Document-Series design provides a **theme customizer** (SubPhase-10), which is fundamentally different from a **template system**:

| Concept            | Theme Customizer (Current)                              | Template System (Missing)                       |
| ------------------ | ------------------------------------------------------- | ----------------------------------------------- |
| What it does       | Tweak colors, fonts, logos on a **single fixed layout** | Choose from **multiple complete store designs** |
| Comparable to      | WordPress Customizer panel                              | Shopify Theme Store                             |
| Layout flexibility | Homepage section order only (5 fixed types)             | Completely different page layouts per template  |
| Effort to switch   | Gradual tweaks                                          | One-click complete redesign                     |
| Tenant experience  | "Customize your store"                                  | "Choose a store design, then customize"         |

### What the Current Theme Engine Provides

```
CURRENT ARCHITECTURE (Theme Customizer Only):

┌─────────────────────────────┐
│      Tenant Store Setup     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│    Theme Customizer Panel    │
│                             │
│  ● Colors (5 values)        │
│  ● Fonts (2 selections)     │
│  ● Logo (3 variants)        │
│  ● Homepage (5 sections     │
│    with drag-and-drop)      │
│  ● Announcement bar         │
│  ● Draft / Preview / Publish│
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   Single Layout Structure    │
│                             │
│   Header → Content → Footer │
│   (No alternative layouts)  │
└─────────────────────────────┘
```

### Homepage Section Types (Hardcoded — 5 total)

| Section           | Configurable Fields                      |
| ----------------- | ---------------------------------------- |
| Hero Banner       | Image, title, subtitle, CTA text + link  |
| Featured Products | Title, count, source, columns            |
| Categories Grid   | Title, categories, style (grid/carousel) |
| Testimonials      | Title, items, style (cards/carousel)     |
| Newsletter        | Title, subtitle, button, background      |

**Key Limitation:** "Add Section" (Task 76) allows adding from this predefined list only. There is **no custom section creation** and **no third-party section plugins**.

### What's Missing for a Full Template System

```
WHAT WOULD BE NEEDED:

┌─────────────────────────────────────────────────────────────────┐
│                   TEMPLATE SYSTEM (Proposed)                     │
│                                                                 │
│  1. TEMPLATE REGISTRY                                           │
│     ├── ThemeTemplate model (name, category, preview, JSON)    │
│     ├── Template categories (Electronics, Fashion, Food, etc.)  │
│     └── Version management (template updates)                  │
│                                                                 │
│  2. TEMPLATE SELECTION UI                                       │
│     ├── "Choose a Template" step in store setup                │
│     ├── Visual grid of template previews                       │
│     ├── Live preview before applying                           │
│     └── "Use This Template" one-click apply                    │
│                                                                 │
│  3. LAYOUT VARIANTS (per template)                              │
│     ├── Different header styles (standard, centered, minimal)  │
│     ├── Different product grid layouts (masonry, cards, list)  │
│     ├── Different product detail layouts (gallery, full-width) │
│     ├── Different footer styles (simple, mega, minimal)        │
│     └── Different homepage arrangements (hero-first, grid-first)│
│                                                                 │
│  4. TEMPLATE APPLICATION FLOW                                   │
│     ├── Copy template JSON into tenant's theme settings        │
│     ├── Tenant customizes on top of template                   │
│     └── "Reset to Template Default" option                     │
│                                                                 │
│  5. TEMPLATE MARKETPLACE (future)                               │
│     ├── Community templates                                    │
│     ├── Premium templates                                      │
│     └── Template sharing/export                                │
└─────────────────────────────────────────────────────────────────┘
```

### Why Adding Templates is LOW Risk

The existing Theme Engine stores settings as a **JSON blob per tenant**. Templates would simply be **pre-defined JSON configurations**:

```
Template = Pre-defined Theme JSON + Layout Variant Identifier

Current Flow:
  Tenant → Customizer → Save JSON → Render

Proposed Flow:
  Tenant → Pick Template → Copy Template JSON → Customizer → Save JSON → Render
                                                 (optional tweaks)
```

No new rendering engine is needed. The same CSS variables, components, and homepage section builder work identically.

---

## 20. Plugin & Extensibility Analysis

> **Question: Is the webstore plugin-based?**
> **Answer: NO — it is a monolithic fixed-feature system.**

### Current Extensibility Model

```
CURRENT ARCHITECTURE (Monolithic):

┌─────────────────────────────────────────────────────────────┐
│                 ALL FEATURES ARE HARDCODED                    │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ Feature Flags    │  │ Subscription Plan │                │
│  │ (platform admin) │  │ Gating            │                │
│  │                  │  │                  │                 │
│  │ Toggle on/off    │  │ Basic: 5 features│                 │
│  │ per tenant       │  │ Pro: 15 features │                 │
│  │                  │  │ Enterprise: all   │                 │
│  └──────────────────┘  └──────────────────┘                │
│                                                             │
│  NO plugin installation  |  NO extension registry          │
│  NO widget marketplace   |  NO third-party modules         │
│  NO hook/event system    |  NO custom code injection       │
└─────────────────────────────────────────────────────────────┘
```

### Existing Patterns That Resemble Extensibility

| Pattern                    | Where                             | What It Is                                       | What It's NOT                          |
| -------------------------- | --------------------------------- | ------------------------------------------------ | -------------------------------------- |
| Feature Flags              | `docs/saas/feature-flags.md`      | Platform-admin toggles with `rollout_percentage` | NOT tenant-installed plugins           |
| Abstract Payment Processor | Phase-09, SubPhase-01             | Developer-added payment gateways via ABC pattern | NOT tenant-activatable payment plugins |
| Homepage Section Builder   | Phase-08, SubPhase-10             | 5 hardcoded section types with drag-and-drop     | NOT custom widget/section plugins      |
| CMS Content Blocks         | Phase-08, SubPhase-11             | Image, video, quote, list, table blocks          | NOT third-party content block plugins  |
| Subscription Plans         | `docs/saas/subscription-plans.md` | Feature gating per plan tier                     | NOT an app/plugin marketplace          |

### What a Plugin System Would Require

```
PLUGIN ARCHITECTURE (If Designed):

┌─────────────────────────────────────────────────────────────────┐
│                     PLUGIN SYSTEM                                │
│                                                                 │
│  REGISTRY LAYER                                                 │
│  ├── PluginManifest model (name, version, hooks, slots, config)│
│  ├── PluginInstallation per-tenant tracking                    │
│  ├── Plugin lifecycle: install → activate → deactivate → uninstall│
│  └── Dependency resolution between plugins                     │
│                                                                 │
│  UI INJECTION LAYER                                             │
│  ├── <PluginSlot name="header-after" />                        │
│  ├── <PluginSlot name="product-page-after-price" />            │
│  ├── <PluginSlot name="cart-page-before-total" />              │
│  ├── <PluginSlot name="checkout-after-payment" />              │
│  └── <PluginSlot name="footer-before" />                       │
│                                                                 │
│  BACKEND HOOK LAYER                                             │
│  ├── on_order_placed(order) → plugin processes                 │
│  ├── on_payment_completed(payment) → plugin processes          │
│  ├── on_product_viewed(product) → analytics plugins            │
│  └── on_customer_registered(customer) → welcome plugins        │
│                                                                 │
│  CONFIGURATION LAYER                                            │
│  ├── Per-plugin settings schema (JSON schema)                  │
│  ├── Plugin settings UI (auto-generated from schema)           │
│  └── Plugin data isolation per tenant                          │
│                                                                 │
│  SANDBOXING                                                     │
│  ├── iframe isolation for UI plugins                           │
│  ├── Limited API access per plugin                             │
│  └── Resource quotas                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Comparison: Current vs Plugin-Based

| Aspect             | Current (Fixed)                         | Plugin-Based                               |
| ------------------ | --------------------------------------- | ------------------------------------------ |
| New features       | Developer implements, deploys globally  | Tenant installs from marketplace           |
| Payment gateways   | Developer adds in code                  | Plugin per gateway                         |
| Shipping providers | Developer adds in code                  | Plugin per provider                        |
| Analytics tools    | Developer adds Google Analytics in code | Plugin: GA, Mixpanel, Hotjar, etc.         |
| Chat widgets       | Hardcoded WhatsApp widget               | Plugin: WhatsApp, Tawk.to, Intercom, etc.  |
| Marketing tools    | Hardcoded coupons/flash sales           | Plugin: advanced email, SMS, loyalty, etc. |
| Dev effort         | Lower initial, higher per-feature       | Higher initial, lower per-feature          |

### Recommendation

A full plugin system is a **Phase 11+ feature** — it requires significant infrastructure. However, we can prepare for it during Phase 08 by:

1. Using **composition patterns** (render slots) in the layout
2. Keeping features **modular** internally (each feature as a self-contained module)
3. Defining **clear interfaces** between modules via TypeScript types
4. Using **feature flags** as the precursor to plugin activation

---

## 21. Pre-Built Template Strategy

> **Question: Can we create template storefronts during development?**
> **Answer: YES — and this is a highly efficient parallel development strategy.**

### Strategy Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              PARALLEL TEMPLATE DEVELOPMENT STRATEGY              │
│                                                                 │
│  WHEN: During Phase 08 development (SubPhases 01-14)            │
│  WHO: Design team / Junior devs working alongside core devs    │
│  WHAT: Create 4-6 complete theme JSON configs + CSS variations │
│  HOW: Use the Theme Engine's JSON structure as the blueprint   │
│                                                                 │
│  Timeline:                                                      │
│                                                                 │
│  Phase 08 Core Dev ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│  SP01-02 ▓▓▓▓                                                   │
│  SP03-04     ▓▓▓▓▓▓                                             │
│  SP05            ▓▓▓                                             │
│  SP06-07             ▓▓▓▓▓▓                                     │
│  SP08-09                   ▓▓▓▓▓▓                               │
│  SP10                            ▓▓▓▓  ← Theme Engine built    │
│  SP11-14                             ▓▓▓▓▓▓▓▓                  │
│                                                                 │
│  Template Dev    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━        │
│  Research    ░░░░░                                               │
│  Design          ░░░░░░░░░░                                     │
│  Build                     ░░░░░░░░░░░  ← After SP10           │
│  Polish                              ░░░░░░░░                   │
│  QA/Test                                     ░░░░               │
└─────────────────────────────────────────────────────────────────┘
```

### Proposed Templates (6 Industry-Specific)

```
┌─────────────────────────────────────────────────────────────────┐
│                  TEMPLATE CATALOG                                │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │   🔌 TECHMART   │  │   👗 FASHIONLK  │  │  🍛 SPICEHUB   │ │
│  │                 │  │                 │  │                │ │
│  │ Electronics &   │  │ Fashion &       │  │ Food, Spices & │ │
│  │ Gadgets store   │  │ Apparel store   │  │ Grocery store  │ │
│  │                 │  │                 │  │                │ │
│  │ Colors:         │  │ Colors:         │  │ Colors:        │ │
│  │ #2563eb blue    │  │ #ec4899 pink    │  │ #ea580c orange │ │
│  │ #1f2937 dark    │  │ #f8fafc light   │  │ #365314 green  │ │
│  │                 │  │                 │  │                │ │
│  │ Fonts:          │  │ Fonts:          │  │ Fonts:         │ │
│  │ Inter + Roboto  │  │ Playfair +      │  │ Poppins +      │ │
│  │                 │  │ Lato            │  │ Nunito         │ │
│  │                 │  │                 │  │                │ │
│  │ Homepage:       │  │ Homepage:       │  │ Homepage:      │ │
│  │ Hero → Products │  │ Hero → Cats →   │  │ Cats → Hero →  │ │
│  │ → Cats → News   │  │ Products → Test │  │ Products →     │ │
│  │                 │  │                 │  │ Testimonials   │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │  🏠 HOMEWARE    │  │  💊 WELLNESS    │  │  🎁 GENERAL    │ │
│  │                 │  │                 │  │                │ │
│  │ Home & Living   │  │ Health &        │  │ Multi-category │ │
│  │ Furniture store │  │ Beauty store    │  │ General store  │ │
│  │                 │  │                 │  │                │ │
│  │ Colors:         │  │ Colors:         │  │ Colors:        │ │
│  │ #78716c warm    │  │ #059669 teal    │  │ #7c3aed purple │ │
│  │ #f5f5f4 stone   │  │ #f0fdf4 mint   │  │ #fafaf9 neutral│ │
│  │                 │  │                 │  │                │ │
│  │ Fonts:          │  │ Fonts:          │  │ Fonts:         │ │
│  │ DM Serif +      │  │ Quicksand +    │  │ Space Grotesk +│ │
│  │ DM Sans         │  │ Source Sans    │  │ DM Sans        │ │
│  │                 │  │                 │  │                │ │
│  │ Homepage:       │  │ Homepage:       │  │ Homepage:      │ │
│  │ Hero → Test →   │  │ Hero → Products│  │ Hero → Cats →  │ │
│  │ Cats → Products │  │ → Test → News  │  │ Products →     │ │
│  │                 │  │                 │  │ News           │ │
│  └─────────────────┘  └─────────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Template JSON Structure (Enhanced)

Each template is a complete `ThemeTemplate` JSON file:

```json
{
  "id": "techmart-v1",
  "name": "TechMart",
  "category": "electronics",
  "version": "1.0.0",
  "description": "Bold, modern template for electronics and gadget stores",
  "preview": "/templates/techmart/preview.png",
  "thumbnail": "/templates/techmart/thumb.png",
  "tags": ["electronics", "modern", "bold", "dark-header"],

  "theme": {
    "colors": {
      "primary": "#2563eb",
      "secondary": "#1e40af",
      "accent": "#f59e0b",
      "background": "#ffffff",
      "surface": "#f8fafc",
      "text": "#1f2937",
      "textMuted": "#6b7280",
      "border": "#e5e7eb",
      "success": "#10b981",
      "warning": "#f59e0b",
      "error": "#ef4444"
    },
    "fonts": {
      "heading": { "family": "Inter", "weights": [500, 600, 700] },
      "body": { "family": "Roboto", "weights": [400, 500] }
    },
    "borderRadius": "0.5rem",
    "spacing": "comfortable"
  },

  "logo": {
    "desktop": null,
    "mobile": null,
    "favicon": null,
    "maxHeight": "48px"
  },

  "layout": {
    "header": {
      "style": "standard",
      "sticky": true,
      "transparent": false
    },
    "footer": {
      "style": "mega",
      "columns": 4
    },
    "productGrid": {
      "columns": { "mobile": 2, "tablet": 3, "desktop": 4 },
      "cardStyle": "standard",
      "showRating": true,
      "showQuickAdd": true
    },
    "productDetail": {
      "galleryPosition": "left",
      "galleryStyle": "thumbnails",
      "tabStyle": "underline"
    }
  },

  "homepage": {
    "sections": [
      {
        "type": "hero",
        "enabled": true,
        "order": 1,
        "config": {
          "height": "500px",
          "overlay": true,
          "overlayOpacity": 0.4,
          "textAlignment": "left"
        }
      },
      {
        "type": "featured_products",
        "enabled": true,
        "order": 2,
        "config": {
          "title": "Featured Products",
          "count": 8,
          "columns": 4,
          "source": "featured"
        }
      },
      {
        "type": "categories",
        "enabled": true,
        "order": 3,
        "config": {
          "title": "Shop by Category",
          "style": "grid",
          "columns": 3
        }
      },
      {
        "type": "newsletter",
        "enabled": true,
        "order": 4,
        "config": {
          "title": "Stay Updated",
          "subtitle": "Get the latest deals and product news",
          "backgroundColor": "#1f2937"
        }
      }
    ]
  },

  "announcement": {
    "enabled": true,
    "text": "Free shipping on all electronics over ₨10,000",
    "backgroundColor": "#2563eb",
    "textColor": "#ffffff",
    "dismissible": true
  }
}
```

### Template Development Pipeline

```
TEMPLATE CREATION WORKFLOW:

Step 1: DESIGN (Figma/Sketch — parallel to SP01-SP09)
  ├── Color palette selection
  ├── Font pairing selection
  ├── Homepage mockup (mobile + desktop)
  ├── Product page mockup
  └── Category page mockup

Step 2: JSON CONFIG (After SP10 Theme Engine is built)
  ├── Create template JSON file from design
  ├── Define all theme variables
  ├── Set homepage section configuration
  └── Set layout variant options

Step 3: CSS VARIANTS (Optional — for deeper customization)
  ├── Header style variations (standard, centered, minimal)
  ├── Product card style variations
  ├── Footer style variations
  └── Button style variations

Step 4: PREVIEW ASSETS
  ├── Full-page screenshot (desktop)
  ├── Full-page screenshot (mobile)
  ├── Thumbnail for template picker
  └── Color palette swatch image

Step 5: QA & INTEGRATION
  ├── Apply template to test tenant
  ├── Verify all pages render correctly
  ├── Test mobile responsiveness
  ├── Test customizer after template applied
  └── Add to template registry
```

### Where Templates Would Live

```
frontend/
├── data/
│   └── templates/
│       ├── index.ts                    # Template registry (exports all)
│       ├── techmart.json               # Electronics template
│       ├── fashionlk.json              # Fashion template
│       ├── spicehub.json               # Food/Grocery template
│       ├── homeware.json               # Home & Living template
│       ├── wellness.json               # Health & Beauty template
│       └── general.json                # General multi-category template
│
├── public/templates/
│   ├── techmart/
│   │   ├── preview.png                 # Full-page preview
│   │   └── thumb.png                   # Thumbnail
│   ├── fashionlk/
│   │   ├── preview.png
│   │   └── thumb.png
│   └── ... (one folder per template)
│
├── components/storefront/theme/
│   ├── TemplatePicker.tsx              # Grid of template cards
│   ├── TemplatePreview.tsx             # Preview modal
│   └── TemplateApplyButton.tsx         # "Use This Template"
│
└── lib/store/
    └── templateUtils.ts                # Apply template, merge with overrides
```

### Template Picker UI

```
┌─────────────────────────────────────────────────────────────────┐
│  CHOOSE A TEMPLATE FOR YOUR STORE                               │
│  Select a starting point, then customize colors and content     │
│                                                                 │
│  Filter: [All] [Electronics] [Fashion] [Food] [Home] [Health]  │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│  │ ┌───────────┐ │  │ ┌───────────┐ │  │ ┌───────────┐ │      │
│  │ │           │ │  │ │           │ │  │ │           │ │      │
│  │ │  Preview  │ │  │ │  Preview  │ │  │ │  Preview  │ │      │
│  │ │  Image    │ │  │ │  Image    │ │  │ │  Image    │ │      │
│  │ │           │ │  │ │           │ │  │ │           │ │      │
│  │ └───────────┘ │  │ └───────────┘ │  │ └───────────┘ │      │
│  │               │  │               │  │               │      │
│  │ TechMart      │  │ FashionLK     │  │ SpiceHub      │      │
│  │ Electronics   │  │ Fashion       │  │ Food & Grocery│      │
│  │ ⭐ Popular    │  │               │  │               │      │
│  │               │  │               │  │               │      │
│  │ [Preview]     │  │ [Preview]     │  │ [Preview]     │      │
│  │ [Use This →]  │  │ [Use This →]  │  │ [Use This →]  │      │
│  └───────────────┘  └───────────────┘  └───────────────┘      │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│  │ HomeWare      │  │ Wellness      │  │ General       │      │
│  │ Home & Living │  │ Health & Beauty│  │ Multi-Category│      │
│  │ ...           │  │ ...           │  │ ...           │      │
│  └───────────────┘  └───────────────┘  └───────────────┘      │
│                                                                 │
│  [Skip — Start from Scratch →]                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Time Savings Estimate

| Without Templates                                                      | With Templates                                                          |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Tenant signs up → blank store → must configure everything from scratch | Tenant signs up → picks template → store looks professional immediately |
| 30-60 min to set up colors, fonts, sections                            | 2 min to select + 10 min to customize                                   |
| Many tenants leave store looking generic/broken                        | All stores start with a polished, industry-appropriate design           |
| Higher churn during setup                                              | Lower churn, faster time-to-launch                                      |

---

## 22. Additional Architecture Details

### Multi-Tenant Routing

```
REQUEST FLOW (Tenant Resolution):

Browser: https://mystore.lankacommerce.cloud/products
         ─────────────────────────────────────────────
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│  Next.js Middleware (middleware.ts)                      │
│                                                         │
│  1. Extract subdomain: "mystore"                        │
│  2. Lookup tenant by subdomain → TenantConfig           │
│  3. Inject tenant context into request headers          │
│  4. Route to (storefront)/ route group                  │
│                                                         │
│  Custom Domains:                                        │
│  mystore.com → CNAME → mystore.lankacommerce.cloud     │
│  → Middleware resolves custom domain → same tenant      │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  (storefront)/layout.tsx                                │
│                                                         │
│  1. Read tenant from headers/context                    │
│  2. Fetch tenant theme settings (cached)                │
│  3. Wrap children in <ThemeProvider>                     │
│  4. Inject CSS variables                                │
│  5. Load Google Fonts dynamically                       │
│  6. Render <Header> + {children} + <Footer>             │
└─────────────────────────────────────────────────────────┘
```

### Data Architecture (Backend Models)

```
WEBSTORE-RELATED MODELS:

┌──────────────────┐     ┌──────────────────┐
│ Tenant           │────►│ StoreSettings    │
│                  │     │                  │
│ name             │     │ theme_json       │  ← Theme JSON blob
│ subdomain        │     │ template_id      │  ← Template reference
│ custom_domain    │     │ announcement     │
│ plan             │     │ seo_defaults     │
│ is_active        │     │ social_links     │
└──────────────────┘     └──────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│ Product          │     │ Category         │
│                  │     │                  │
│ name, slug       │     │ name, slug       │
│ description      │     │ parent           │
│ price, sale_price│     │ image            │
│ sku              │     │ description      │
│ images[]         │     │ is_active        │
│ variants[]       │     └──────────────────┘
│ category         │
│ collections[]    │     ┌──────────────────┐
│ is_active        │     │ Collection       │
│ avg_rating       │     │                  │
│ sales_count      │     │ name, slug       │
└──────┬───────────┘     │ products[]       │
       │                  │ description      │
       │                  └──────────────────┘
       ▼
┌──────────────────┐     ┌──────────────────┐
│ ProductVariant   │     │ ProductImage     │
│                  │     │                  │
│ product          │     │ product          │
│ sku              │     │ image            │
│ price_override   │     │ alt_text         │
│ stock_quantity   │     │ is_primary       │
│ attributes       │     │ sort_order       │
│ (size, color)    │     └──────────────────┘
└──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ Order            │     │ OrderItem        │
│                  │     │                  │
│ order_number     │     │ order            │
│ customer         │     │ product          │
│ status           │     │ variant          │
│ shipping_address │     │ quantity         │
│ payment_method   │     │ unit_price       │
│ total            │     │ total_price      │
│ tracking_number  │     └──────────────────┘
└──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ Customer         │     │ Address          │
│                  │     │                  │
│ user (FK)        │     │ customer         │
│ phone            │     │ province         │
│ whatsapp_enabled │     │ district         │
│ default_address  │     │ city             │
│ marketing_optin  │     │ address_line_1   │
└──────────────────┘     │ address_line_2   │
                          │ landmark         │
                          │ is_default       │
                          └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ Review           │     │ Wishlist         │
│                  │     │                  │
│ product          │     │ customer         │
│ customer         │     │ product          │
│ rating (1-5)     │     │ added_at         │
│ title            │     └──────────────────┘
│ content          │
│ is_verified      │     ┌──────────────────┐
└──────────────────┘     │ Coupon           │
                          │                  │
┌──────────────────┐     │ code             │
│ FlashSale        │     │ discount_type    │
│                  │     │ discount_value   │
│ name             │     │ min_order        │
│ start_date       │     │ usage_limit      │
│ end_date         │     │ is_active        │
│ products[]       │     │ valid_from       │
│ discount_percent │     │ valid_until      │
│ is_active        │     └──────────────────┘
└──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│ CMSPage          │     │ BlogPost         │
│                  │     │                  │
│ title, slug      │     │ title, slug      │
│ content (rich)   │     │ content (rich)   │
│ seo_title        │     │ featured_image   │
│ seo_description  │     │ author           │
│ is_published     │     │ tags[]           │
│ template         │     │ is_published     │
└──────────────────┘     │ published_at     │
                          └──────────────────┘
```

### Security Architecture

```
STOREFRONT SECURITY:

┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
│                                                                 │
│  1. AUTHENTICATION                                              │
│     ├── JWT (access token: 15 min, refresh: 7-30 days)         │
│     ├── httpOnly cookies (no localStorage for tokens)           │
│     ├── CSRF protection on state-changing requests              │
│     ├── Rate limiting on login (5 attempts / 15 min)           │
│     └── Account lockout after consecutive failures              │
│                                                                 │
│  2. TENANT ISOLATION                                            │
│     ├── Middleware validates tenant on every request             │
│     ├── All queries scoped by tenant_id automatically          │
│     ├── No cross-tenant data leakage                           │
│     └── Tenant-specific API keys for payment gateways          │
│                                                                 │
│  3. INPUT VALIDATION                                            │
│     ├── Zod schemas on all form inputs (client-side)           │
│     ├── DRF serializers validate all API inputs (server-side)  │
│     ├── File upload: type + size validation                    │
│     └── SQL injection protection (Django ORM)                   │
│                                                                 │
│  4. PAYMENT SECURITY                                            │
│     ├── PCI compliance via payment gateway redirects            │
│     ├── No credit card data stored locally                     │
│     ├── Webhook signature verification                         │
│     └── HTTPS-only for all transactions                         │
│                                                                 │
│  5. API PROTECTION                                              │
│     ├── Public endpoints: product listing, search, categories  │
│     ├── Auth-required: cart sync, orders, profile, wishlist     │
│     ├── Rate limiting per IP + per token                       │
│     └── CORS configured per tenant domain                      │
└─────────────────────────────────────────────────────────────────┘
```

### Error Handling Strategy

```
ERROR BOUNDARY ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────┐
│  (storefront)/                                                  │
│  ├── error.tsx          ← Global error boundary (500)          │
│  ├── not-found.tsx      ← Global 404 page                     │
│  ├── loading.tsx        ← Global loading skeleton              │
│  │                                                              │
│  ├── products/                                                  │
│  │   ├── error.tsx      ← Product listing error                │
│  │   └── loading.tsx    ← Product grid skeleton                │
│  │                                                              │
│  ├── checkout/                                                  │
│  │   ├── error.tsx      ← Checkout error (don't lose cart!)    │
│  │   └── loading.tsx    ← Checkout skeleton                    │
│  │                                                              │
│  └── account/                                                   │
│      ├── error.tsx      ← Account error                        │
│      └── loading.tsx    ← Account skeleton                     │
│                                                                 │
│  Error Recovery:                                                │
│  ├── "Try Again" button on error pages                         │
│  ├── Cart preserved in localStorage even on errors             │
│  ├── Checkout progress preserved in URL params                 │
│  ├── Toast notifications for non-critical errors               │
│  └── Sentry error reporting (Phase 10)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Caching Strategy

```
CACHE LAYERS:

┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐
│   Browser     │  │   CDN Edge    │  │   Next.js     │  │   Redis      │
│   (Client)    │  │   (Vercel/CF) │  │   (Server)    │  │   (Backend)  │
│               │  │               │  │               │  │              │
│ localStorage: │  │ Static assets │  │ ISR pages     │  │ Query cache  │
│ • Cart        │  │ Images (CDN)  │  │ Product pages │  │ Session data │
│ • Searches    │  │ CSS/JS        │  │ Category pages│  │ Rate limits  │
│ • Recently    │  │ Font files    │  │ CMS pages     │  │ Feature flags│
│   viewed      │  │               │  │               │  │              │
│               │  │ Cache-Control │  │ revalidate:   │  │ TTL per key  │
│ TanStack Q:   │  │ immutable for │  │ 60s products  │  │ 5m products  │
│ • Products    │  │ hashed assets │  │ 300s category │  │ 1h categories│
│ • Categories  │  │ 1y max-age    │  │ 3600s CMS     │  │ 24h CMS     │
│ • User data   │  │               │  │               │  │              │
└───────────────┘  └───────────────┘  └───────────────┘  └──────────────┘
```

### Mobile Responsiveness

```
RESPONSIVE BREAKPOINTS:

┌────────────────────────────────────────────────────────────────┐
│  Tailwind Default + Custom:                                     │
│                                                                │
│  sm:  640px   ← Small phones (portrait)                        │
│  md:  768px   ← Tablets                                        │
│  lg:  1024px  ← Laptops                                        │
│  xl:  1280px  ← Desktops                                       │
│  2xl: 1536px  ← Large screens                                  │
│                                                                │
│  MOBILE-FIRST APPROACH:                                        │
│  ├── Default styles = mobile                                   │
│  ├── sm: → minor adjustments                                   │
│  ├── md: → tablet layout (2-3 columns)                         │
│  ├── lg: → desktop layout (sidebar + content)                  │
│  └── xl: → max-width container                                 │
│                                                                │
│  MOBILE-SPECIFIC FEATURES:                                     │
│  ├── Hamburger menu → full-screen drawer                       │
│  ├── Bottom sheet for filters (instead of sidebar)             │
│  ├── Swipeable image gallery                                   │
│  ├── Sticky "Add to Cart" bar on product page                  │
│  ├── Tap-to-call and WhatsApp deep links                       │
│  ├── Touch-optimized buttons (min 44x44px)                     │
│  └── Pull-to-refresh on listings                               │
└────────────────────────────────────────────────────────────────┘
```

---

## 23. SubPhase Dependencies

### Dependency Graph

```
Phase 07 (Frontend Setup)
    │
    ▼
SubPhase-01 (Project Structure)
    │
    ▼
SubPhase-02 (Storefront Layout)
    │
    ├──────────────────────┬─────────────────────┐
    ▼                      ▼                     ▼
SubPhase-03            SubPhase-08           SubPhase-10
(Product Catalog)      (Customer Auth)       (Theme Engine)
    │                      │                     │
    ▼                      ▼                     │
SubPhase-04            SubPhase-09               │
(Product Detail)       (Customer Portal)         │
    │                                            │
    ├──────────────────────┬─────────────────────┘
    ▼                      ▼
SubPhase-05            SubPhase-11
(Search)               (Static Pages & CMS)
    │                      │
    └──────────┬───────────┘
               ▼
SubPhase-06 (Shopping Cart)
               │
               ▼
SubPhase-07 (Checkout Flow)  ◄──── Phase 09 (Payment integrations)
               │
               ▼
SubPhase-12 (SEO)
               │
               ▼
SubPhase-13 (Performance)
               │
               ▼
SubPhase-14 (Marketing Features)
```

### Cross-Phase Dependencies

| Dependency                  | Source   | Target               |
| --------------------------- | -------- | -------------------- |
| Next.js project setup       | Phase 07 | SubPhase 01          |
| Payment gateway integration | Phase 09 | SubPhase 07 (stubs)  |
| Shipping API integration    | Phase 09 | SubPhase 07 (stubs)  |
| Sinhala-glish search        | Phase 10 | SubPhase 05 (future) |

---

## 24. Task Breakdown Summary

| SubPhase  | Name                       | Tasks      | Focus                                            |
| --------- | -------------------------- | ---------- | ------------------------------------------------ |
| 01        | Webstore Project Structure | 88         | Route groups, directory structure, shared config |
| 02        | Storefront Layout          | 94         | Header, footer, navigation, mobile menu          |
| 03        | Product Catalog Pages      | 96         | Category/collection pages, filters, sort, grid   |
| 04        | Product Detail Page        | 94         | Gallery, variants, reviews, related products     |
| 05        | Search Functionality       | 92         | Autocomplete, suggestions, results, recent       |
| 06        | Shopping Cart              | 96         | Cart CRUD, mini cart, persistence, coupons       |
| 07        | Checkout Flow              | 98         | 5-step wizard, Sri Lanka address, payments       |
| 08        | Customer Authentication    | 94         | Register, login, JWT, social login stubs         |
| 09        | Customer Portal            | 96         | Dashboard, orders, addresses, wishlist           |
| 10        | Theme Engine               | 92         | Colors, fonts, logo, homepage builder, preview   |
| 11        | Static Pages & CMS         | 94         | About, contact, FAQ, blog, rich text editor      |
| 12        | SEO Implementation         | 92         | Meta tags, structured data, sitemap, robots      |
| 13        | Performance Optimization   | 94         | Images, code splitting, ISR, caching             |
| 14        | Marketing Features         | 96         | Coupons, flash sales, WhatsApp, newsletters      |
| **TOTAL** |                            | **~1,316** |                                                  |

---

## 25. Key File Paths Reference

### Frontend

| Purpose             | Path                                  |
| ------------------- | ------------------------------------- |
| Storefront routes   | `frontend/app/(storefront)/`          |
| Store components    | `frontend/components/storefront/`     |
| Shared components   | `frontend/components/shared/`         |
| Zustand stores      | `frontend/stores/storefront/`         |
| Custom hooks        | `frontend/hooks/storefront/`          |
| API services        | `frontend/services/storefront/`       |
| TypeScript types    | `frontend/types/storefront/`          |
| Store config        | `frontend/lib/store/config.ts`        |
| Store routes        | `frontend/lib/store/routes.ts`        |
| Store utilities     | `frontend/lib/store/utils.ts`         |
| SEO utilities       | `frontend/lib/seo/`                   |
| Sri Lanka data      | `frontend/data/srilanka/`             |
| Theme CSS variables | `frontend/styles/theme/variables.css` |
| Theme defaults      | `frontend/styles/theme/defaults.ts`   |
| Dynamic sitemap     | `frontend/app/sitemap.ts`             |
| Robots.txt          | `frontend/app/robots.ts`              |

### Backend

| Purpose             | Path                      |
| ------------------- | ------------------------- |
| Webstore Django app | `backend/apps/webstore/`  |
| Products app        | `backend/apps/products/`  |
| Orders app          | `backend/apps/orders/`    |
| Customers app       | `backend/apps/customers/` |
| Inventory app       | `backend/apps/inventory/` |

### Documentation

| Purpose            | Path                                                    |
| ------------------ | ------------------------------------------------------- |
| Phase 08 docs      | `Document-Series/Phase-08_Webstore-Ecommerce-Platform/` |
| SubPhase summaries | `Document-Series/Phase-08_.../00_SUBPHASES_SUMMARY.md`  |
| Architecture docs  | `docs/architecture/`                                    |

---

> **Document End** — This architecture document was generated by analyzing all 14 SubPhase documents in Phase-08 of the Document-Series. The webstore is currently in the planning stage with 0% implementation. All architecture decisions, component structures, and technical details are derived from the project's Document-Series specifications.
