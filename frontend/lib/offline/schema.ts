// ================================================================
// IndexedDB Schema & Entity Interfaces — Task 18
// ================================================================
// Defines all object store schemas, TypeScript interfaces for
// cached entities, and the database upgrade logic.
// ================================================================

// ── Database Config ────────────────────────────────────────────

export const DATABASE_NAME = 'lcc_pos_cache';
export const DATABASE_VERSION = 1;

// ── Object Store Names ─────────────────────────────────────────

export const ObjectStoreNames = {
  PRODUCTS: 'products',
  CATEGORIES: 'categories',
  CUSTOMERS: 'customers',
  SETTINGS: 'settings',
  TRANSACTIONS: 'transactions',
  SYNC_META: 'sync_meta',
} as const;

export type ObjectStoreName =
  (typeof ObjectStoreNames)[keyof typeof ObjectStoreNames];

// ── Entity Interfaces ──────────────────────────────────────────

export interface Product {
  id: string;
  name: string;
  description?: string;
  barcode?: string;
  sku?: string;
  category_id?: string;
  price: number;
  cost?: number;
  tax_rate: number;
  stock_quantity: number;
  images?: string[];
  status: 'active' | 'inactive';
  updated_at: string;
  created_at: string;
}

export interface ProductVariant {
  id: string;
  product_id: string;
  name: string;
  barcode?: string;
  sku?: string;
  price_adjustment: number;
  stock_quantity: number;
  attributes: Record<string, string>;
  updated_at: string;
  created_at: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  parent_id?: string;
  description?: string;
  image?: string;
  sort_order: number;
  status: 'active' | 'inactive';
  updated_at: string;
  created_at: string;
}

export interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
  address?: string;
  loyalty_points: number;
  total_purchases: number;
  tier: 'bronze' | 'silver' | 'gold';
  notes?: string;
  status: 'active' | 'inactive';
  updated_at: string;
  created_at: string;
}

export interface TransactionItem {
  product_id: string;
  variant_id?: string;
  name: string;
  quantity: number;
  unit_price: number;
  discount: number;
  tax: number;
  total: number;
}

export interface Transaction {
  offline_id: string;
  terminal_id: string;
  session_id: string;
  items: TransactionItem[];
  customer_id?: string;
  total: number;
  subtotal: number;
  tax: number;
  payment_method: string;
  status: string;
  sync_status: 'pending' | 'syncing' | 'synced' | 'failed';
  sync_attempts: number;
  last_sync_attempt?: string;
  sync_error?: string;
  server_id?: string;
  created_at: string;
  synced_at?: string;
}

export interface Setting {
  key: string;
  value: unknown;
  updated_at: string;
}

export interface SyncMeta {
  entity_type: string;
  last_sync_at: string;
  version?: string;
  record_count: number;
  sync_token?: string;
  has_more: boolean;
  etag?: string;
  error_count: number;
  last_error?: string;
}

// ── Database Upgrade ───────────────────────────────────────────

/**
 * Called during `onupgradeneeded` to create / migrate object stores.
 * Each version block is additive so the schema evolves incrementally.
 */
export function upgradeDatabaseSchema(
  db: IDBDatabase,
  oldVersion: number
): void {
  if (oldVersion < 1) {
    // ── Products store ───────────────────────────────────────
    const products = db.createObjectStore(ObjectStoreNames.PRODUCTS, {
      keyPath: 'id',
    });
    products.createIndex('barcode', 'barcode', { unique: true });
    products.createIndex('sku', 'sku', { unique: true });
    products.createIndex('name', 'name', { unique: false });
    products.createIndex('category_id', 'category_id', { unique: false });
    products.createIndex('status', 'status', { unique: false });
    products.createIndex('updated_at', 'updated_at', { unique: false });

    // ── Categories store ─────────────────────────────────────
    const categories = db.createObjectStore(ObjectStoreNames.CATEGORIES, {
      keyPath: 'id',
    });
    categories.createIndex('slug', 'slug', { unique: true });
    categories.createIndex('parent_id', 'parent_id', { unique: false });
    categories.createIndex('sort_order', 'sort_order', { unique: false });
    categories.createIndex('updated_at', 'updated_at', { unique: false });

    // ── Customers store ──────────────────────────────────────
    const customers = db.createObjectStore(ObjectStoreNames.CUSTOMERS, {
      keyPath: 'id',
    });
    customers.createIndex('email', 'email', { unique: true });
    customers.createIndex('phone', 'phone', { unique: true });
    customers.createIndex('name', 'name', { unique: false });
    customers.createIndex('tier', 'tier', { unique: false });
    customers.createIndex('status', 'status', { unique: false });
    customers.createIndex('updated_at', 'updated_at', { unique: false });

    // ── Settings store ───────────────────────────────────────
    db.createObjectStore(ObjectStoreNames.SETTINGS, { keyPath: 'key' });

    // ── Transactions store ───────────────────────────────────
    const transactions = db.createObjectStore(ObjectStoreNames.TRANSACTIONS, {
      keyPath: 'offline_id',
    });
    transactions.createIndex('status', 'status', { unique: false });
    transactions.createIndex('sync_status', 'sync_status', { unique: false });
    transactions.createIndex('terminal_id', 'terminal_id', { unique: false });
    transactions.createIndex('created_at', 'created_at', { unique: false });

    // ── Sync meta store ──────────────────────────────────────
    db.createObjectStore(ObjectStoreNames.SYNC_META, {
      keyPath: 'entity_type',
    });
  }

  // Future migrations go here:
  // if (oldVersion < 2) { ... }
}
