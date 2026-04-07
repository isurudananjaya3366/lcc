// ================================================================
// Cache Size Management — Task 29
// ================================================================
// Monitors storage usage and prunes stale data to stay within
// budget.  Runs automatically or on demand.
// ================================================================

import { idbService } from './indexeddb';
import { ObjectStoreNames } from './schema';
import { productsService } from './stores/products';
import { customersService } from './stores/customers';
import { transactionsService } from './stores/transactions';
import { versioningService } from './versioning';

// ── Limits ─────────────────────────────────────────────────────

export const CACHE_LIMITS = {
  MAX_PRODUCTS: 10_000,
  MAX_CUSTOMERS: 5_000,
  MAX_PENDING_TX: 100,
  RECOMMENDED_MB: 50,
} as const;

const SYNCED_TX_MAX_AGE_DAYS = 30;

// ── Types ──────────────────────────────────────────────────────

export interface CacheStats {
  products: number;
  categories: number;
  customers: number;
  settings: number;
  transactions: number;
  syncMeta: number;
  estimatedSizeMB: number;
}

export interface CacheHealthReport {
  healthy: boolean;
  warnings: string[];
}

// ── Service ────────────────────────────────────────────────────

class CacheManager {
  async getCacheStats(): Promise<CacheStats> {
    const [products, categories, customers, settings, transactions, syncMeta] =
      await Promise.all([
        idbService.count(ObjectStoreNames.PRODUCTS),
        idbService.count(ObjectStoreNames.CATEGORIES),
        idbService.count(ObjectStoreNames.CUSTOMERS),
        idbService.count(ObjectStoreNames.SETTINGS),
        idbService.count(ObjectStoreNames.TRANSACTIONS),
        idbService.count(ObjectStoreNames.SYNC_META),
      ]);

    // Rough estimate: ~2KB per product, 1KB per category/customer, 4KB per tx
    const estimatedSizeMB =
      (products * 2 +
        categories * 1 +
        customers * 1 +
        transactions * 4 +
        settings * 0.5) /
      1024;

    return {
      products,
      categories,
      customers,
      settings,
      transactions,
      syncMeta,
      estimatedSizeMB,
    };
  }

  async checkCacheLimits(): Promise<CacheHealthReport> {
    const stats = await this.getCacheStats();
    const warnings: string[] = [];

    if (stats.products > CACHE_LIMITS.MAX_PRODUCTS)
      warnings.push(
        `Products (${stats.products}) exceed limit ${CACHE_LIMITS.MAX_PRODUCTS}`
      );
    if (stats.customers > CACHE_LIMITS.MAX_CUSTOMERS)
      warnings.push(
        `Customers (${stats.customers}) exceed limit ${CACHE_LIMITS.MAX_CUSTOMERS}`
      );
    if (stats.transactions > CACHE_LIMITS.MAX_PENDING_TX)
      warnings.push(
        `Transactions (${stats.transactions}) exceed limit ${CACHE_LIMITS.MAX_PENDING_TX}`
      );
    if (stats.estimatedSizeMB > CACHE_LIMITS.RECOMMENDED_MB)
      warnings.push(
        `Estimated size ${stats.estimatedSizeMB.toFixed(1)}MB exceeds ${CACHE_LIMITS.RECOMMENDED_MB}MB`
      );

    return { healthy: warnings.length === 0, warnings };
  }

  /** Remove oldest inactive products when over limit. */
  async pruneProducts(): Promise<number> {
    const count = await productsService.getProductCount();
    if (count <= CACHE_LIMITS.MAX_PRODUCTS) return 0;

    const all = await productsService.getAllProducts();
    // sort inactive → oldest first
    const candidates = all
      .filter((p) => p.status === 'inactive')
      .sort((a, b) => a.updated_at.localeCompare(b.updated_at));

    const excess = count - CACHE_LIMITS.MAX_PRODUCTS;
    const toRemove = candidates.slice(0, excess);

    if (toRemove.length > 0) {
      await idbService.bulkDelete(
        ObjectStoreNames.PRODUCTS,
        toRemove.map((p) => p.id)
      );
    }
    return toRemove.length;
  }

  /** Remove inactive, non-VIP customers when over limit. */
  async pruneCustomers(): Promise<number> {
    const count = await customersService.getCustomerCount();
    if (count <= CACHE_LIMITS.MAX_CUSTOMERS) return 0;

    const all = await customersService.getAllCustomers();
    const candidates = all
      .filter((c) => c.status === 'inactive' && c.tier === 'bronze')
      .sort((a, b) => a.updated_at.localeCompare(b.updated_at));

    const excess = count - CACHE_LIMITS.MAX_CUSTOMERS;
    const toRemove = candidates.slice(0, excess);

    if (toRemove.length > 0) {
      await idbService.bulkDelete(
        ObjectStoreNames.CUSTOMERS,
        toRemove.map((c) => c.id)
      );
    }
    return toRemove.length;
  }

  /** Remove synced transactions older than 30 days. */
  async pruneSyncedTransactions(): Promise<number> {
    return transactionsService.deleteOldTransactions(SYNCED_TX_MAX_AGE_DAYS);
  }

  /** Run all pruning strategies. */
  async runAutomaticPruning(): Promise<{
    products: number;
    customers: number;
    transactions: number;
  }> {
    const [products, customers, transactions] = await Promise.all([
      this.pruneProducts(),
      this.pruneCustomers(),
      this.pruneSyncedTransactions(),
    ]);
    return { products, customers, transactions };
  }

  /** Full health check — prune + integrity. */
  async performHealthCheck(): Promise<CacheHealthReport> {
    await this.runAutomaticPruning();
    return this.checkCacheLimits();
  }

  /** Wipe all cached data. Transactions are preserved by default. */
  async clearCache(includeTransactions = false): Promise<void> {
    await Promise.all([
      idbService.clear(ObjectStoreNames.PRODUCTS),
      idbService.clear(ObjectStoreNames.CATEGORIES),
      idbService.clear(ObjectStoreNames.CUSTOMERS),
      idbService.clear(ObjectStoreNames.SETTINGS),
      idbService.clear(ObjectStoreNames.SYNC_META),
      ...(includeTransactions
        ? [idbService.clear(ObjectStoreNames.TRANSACTIONS)]
        : []),
    ]);
  }

  /** Query browser Storage API for quota info. */
  async checkStorageQuota(): Promise<{
    usageMB: number;
    quotaMB: number;
    percentUsed: number;
  } | null> {
    if (typeof navigator === 'undefined' || !navigator.storage?.estimate)
      return null;
    const est = await navigator.storage.estimate();
    const usageMB = (est.usage ?? 0) / (1024 * 1024);
    const quotaMB = (est.quota ?? 0) / (1024 * 1024);
    return {
      usageMB: Math.round(usageMB * 100) / 100,
      quotaMB: Math.round(quotaMB * 100) / 100,
      percentUsed:
        quotaMB > 0 ? Math.round((usageMB / quotaMB) * 10000) / 100 : 0,
    };
  }
}

export const cacheManager = new CacheManager();
