/**
 * Cache Configuration — TanStack Query stale/cache times & invalidation mapping.
 */

// ── Stale Time Config (Task 70) ────────────────────────────────
// How long data is considered "fresh" — no background refetch while fresh.

export const STALE_TIMES = {
  /** Cart — always refetch (user-specific, changes frequently) */
  cart: 0,

  /** Products — 5 minutes */
  products: 5 * 60 * 1000,

  /** Categories — 30 minutes (rarely change) */
  categories: 30 * 60 * 1000,

  /** User profile — 10 minutes */
  user: 10 * 60 * 1000,

  /** Search results — 2 minutes */
  search: 2 * 60 * 1000,

  /** Static content (CMS, about, FAQ) — 1 hour */
  static: 60 * 60 * 1000,

  /** Reviews — 15 minutes */
  reviews: 15 * 60 * 1000,

  /** Wishlist — 1 minute */
  wishlist: 60 * 1000,

  /** Orders — 5 minutes */
  orders: 5 * 60 * 1000,

  /** Blog posts — 30 minutes */
  blog: 30 * 60 * 1000,
} as const;

// ── Cache (GC) Time Config (Task 71) ────────────────────────────
// How long data stays in memory after becoming unused.

export const CACHE_TIMES = {
  /** Products — 30 minutes */
  products: 30 * 60 * 1000,

  /** Categories — 1 hour */
  categories: 60 * 60 * 1000,

  /** Cart — 10 minutes */
  cart: 10 * 60 * 1000,

  /** User — 30 minutes */
  user: 30 * 60 * 1000,

  /** Static content — 24 hours */
  static: 24 * 60 * 60 * 1000,

  /** Search — 10 minutes */
  search: 10 * 60 * 1000,

  /** Reviews — 30 minutes */
  reviews: 30 * 60 * 1000,

  /** Blog — 1 hour */
  blog: 60 * 60 * 1000,
} as const;

// ── Query Invalidation Map (Task 72) ────────────────────────────
// Maps mutations to queries that should be invalidated.

export const INVALIDATION_MAP: Record<string, string[]> = {
  // Cart mutations
  'cart.add': ['cart', 'cart-count'],
  'cart.update': ['cart', 'cart-count'],
  'cart.remove': ['cart', 'cart-count'],
  'cart.clear': ['cart', 'cart-count'],
  'cart.applyCoupon': ['cart'],

  // Product mutations (admin)
  'product.create': ['products', 'categories'],
  'product.update': ['products', 'product-detail'],
  'product.delete': ['products', 'categories'],

  // User mutations
  'user.updateProfile': ['user', 'user-profile'],
  'user.updateAddress': ['user', 'addresses'],

  // Wishlist mutations
  'wishlist.add': ['wishlist', 'wishlist-count'],
  'wishlist.remove': ['wishlist', 'wishlist-count'],

  // Review mutations
  'review.create': ['reviews', 'product-detail'],
  'review.update': ['reviews'],
  'review.delete': ['reviews', 'product-detail'],

  // Order mutations
  'order.create': ['orders', 'cart'],
  'order.cancel': ['orders'],
} as const;

export type StaleTimeKey = keyof typeof STALE_TIMES;
export type CacheTimeKey = keyof typeof CACHE_TIMES;
