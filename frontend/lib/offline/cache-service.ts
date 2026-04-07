// ================================================================
// Cache Population Service — Tasks 26, 27 & 30
// ================================================================
// Orchestrates full and incremental sync of server data into
// the local IndexedDB cache.  Also houses cache invalidation.
// ================================================================

import { productsService } from './stores/products';
import { categoriesService } from './stores/categories';
import { customersService } from './stores/customers';
import { settingsService } from './stores/settings';
import { versioningService, type VersionInfo } from './versioning';
import { getCurrentTimestamp } from './utils';
import type { Product, Category, Customer, Setting } from './schema';

// ── Config ─────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

const CACHE_ENDPOINTS = {
  products: `${API_BASE}/pos/cache/products/`,
  categories: `${API_BASE}/pos/cache/categories/`,
  customers: `${API_BASE}/pos/cache/customers/`,
  settings: `${API_BASE}/pos/cache/settings/`,
} as const;

const BATCH_SIZE = 500;
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;
const TIMEOUT_MS = 30_000;

// ── Types ──────────────────────────────────────────────────────

export type SyncMode = 'full' | 'incremental';

export interface SyncProgress {
  entity: string;
  total: number;
  loaded: number;
  percent: number;
}

type ProgressCallback = (progress: SyncProgress) => void;

export type InvalidationReason =
  | 'MANUAL'
  | 'BREAKING_CHANGE'
  | 'CORRUPTION'
  | 'QUOTA_EXCEEDED'
  | 'TOO_OLD'
  | 'SERVER_SIGNAL';

// ── Service ────────────────────────────────────────────────────

class CacheService {
  // ── Full sync orchestration (Task 26) ────────────────────────

  async syncAll(onProgress?: ProgressCallback): Promise<void> {
    await this.syncSettings(onProgress);
    await this.syncCategories('full', onProgress);
    await this.syncProducts('full', onProgress);
    await this.syncCustomers('full', onProgress);
  }

  async syncProducts(
    mode: SyncMode,
    onProgress?: ProgressCallback
  ): Promise<void> {
    const data = await this.fetchEntity<Product>('products', mode, onProgress);
    if (data.length > 0) {
      await productsService.bulkAddProducts(data);
    }
    await versioningService.setEntityVersion('products', {
      last_sync_at: getCurrentTimestamp(),
      record_count: await productsService.getProductCount(),
    });
  }

  async syncCategories(
    mode: SyncMode,
    onProgress?: ProgressCallback
  ): Promise<void> {
    const data = await this.fetchEntity<Category>(
      'categories',
      mode,
      onProgress
    );
    if (data.length > 0) {
      await categoriesService.bulkAddCategories(data);
    }
    await versioningService.setEntityVersion('categories', {
      last_sync_at: getCurrentTimestamp(),
      record_count: await categoriesService.getCategoryCount(),
    });
  }

  async syncCustomers(
    mode: SyncMode,
    onProgress?: ProgressCallback
  ): Promise<void> {
    const data = await this.fetchEntity<Customer>(
      'customers',
      mode,
      onProgress
    );
    if (data.length > 0) {
      await customersService.bulkAddCustomers(data);
    }
    await versioningService.setEntityVersion('customers', {
      last_sync_at: getCurrentTimestamp(),
      record_count: await customersService.getCustomerCount(),
    });
  }

  async syncSettings(onProgress?: ProgressCallback): Promise<void> {
    const data = await this.fetchEntity<Setting>(
      'settings',
      'full',
      onProgress
    );
    if (data.length > 0) {
      const entries: Record<string, unknown> = {};
      for (const s of data) entries[s.key] = s.value;
      await settingsService.bulkSetSettings(entries);
    }
    await versioningService.setEntityVersion('settings', {
      last_sync_at: getCurrentTimestamp(),
      record_count: data.length,
    });
  }

  // ── Batch fetching (Task 26) ─────────────────────────────────

  private async fetchEntity<T>(
    entity: keyof typeof CACHE_ENDPOINTS,
    mode: SyncMode,
    onProgress?: ProgressCallback
  ): Promise<T[]> {
    const results: T[] = [];
    let offset = 0;
    let hasMore = true;

    while (hasMore) {
      const url = new URL(
        CACHE_ENDPOINTS[entity],
        globalThis.location?.origin ?? 'http://localhost'
      );
      url.searchParams.set('limit', String(BATCH_SIZE));
      url.searchParams.set('offset', String(offset));

      const headers: Record<string, string> = {};

      // Incremental sync headers (Task 27)
      if (mode === 'incremental') {
        const meta = await versioningService.getEntityVersion(entity);
        if (meta?.last_sync_at)
          headers['If-Modified-Since'] = meta.last_sync_at;
        if (meta?.sync_token) headers['X-Sync-Token'] = meta.sync_token;
        if (meta?.version) headers['X-Entity-Version'] = meta.version;
      }

      const response = await this.retryWithBackoff(() =>
        this.fetchWithTimeout(url.toString(), { headers })
      );

      // 304 Not Modified — nothing to sync (Task 27)
      if (response.status === 304) {
        await versioningService.setEntityVersion(entity, {
          last_sync_at: getCurrentTimestamp(),
        });
        return results;
      }

      if (!response.ok) {
        throw new Error(
          `Sync ${entity} failed: ${response.status} ${response.statusText}`
        );
      }

      const batch = (await response.json()) as T[];
      results.push(...batch);
      offset += batch.length;

      // Track sync token / has_more from response headers (Task 27)
      const syncToken = response.headers.get('X-Sync-Token');
      const serverHasMore = response.headers.get('X-Has-More');
      if (syncToken) {
        await versioningService.setEntityVersion(entity, {
          sync_token: syncToken,
        });
      }

      hasMore = serverHasMore === 'true' || batch.length === BATCH_SIZE;

      onProgress?.({
        entity,
        total: offset + (hasMore ? BATCH_SIZE : 0),
        loaded: offset,
        percent: hasMore
          ? Math.min(95, Math.round((offset / (offset + BATCH_SIZE)) * 100))
          : 100,
      });

      // Handle deleted records header (Task 27)
      const deletedIdsHeader = response.headers.get('X-Deleted-Ids');
      if (deletedIdsHeader) {
        await this.handleDeletedRecords(entity, deletedIdsHeader.split(','));
      }
    }

    return results;
  }

  // ── Delete handling (Task 27) ────────────────────────────────

  private async handleDeletedRecords(
    entity: string,
    deletedIds: string[]
  ): Promise<void> {
    const { idbService } = await import('./indexeddb');
    await idbService.bulkDelete(entity, deletedIds);
  }

  // ── Retry logic (Task 26) ───────────────────────────────────

  private async retryWithBackoff<T>(fn: () => Promise<T>): Promise<T> {
    let lastError: unknown;
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        if (attempt < MAX_RETRIES - 1) {
          await this.sleep(RETRY_DELAY_MS * 2 ** attempt);
        }
      }
    }
    throw lastError;
  }

  private fetchWithTimeout(url: string, init?: RequestInit): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    return fetch(url, { ...init, signal: controller.signal }).finally(() =>
      clearTimeout(timer)
    );
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ── Cache Invalidation (Task 30) ─────────────────────────────

  async invalidateEntity(
    entityType: string,
    reason: InvalidationReason = 'MANUAL'
  ): Promise<void> {
    const { idbService } = await import('./indexeddb');
    await idbService.clear(entityType);
    await versioningService.resetEntityVersion(entityType);
    this.logInvalidation(entityType, reason);
    await this.cascadeInvalidation(entityType);
  }

  async invalidateAll(reason: InvalidationReason = 'MANUAL'): Promise<void> {
    const entities = ['products', 'categories', 'customers', 'settings'];
    for (const entity of entities) {
      const { idbService } = await import('./indexeddb');
      await idbService.clear(entity);
      await versioningService.resetEntityVersion(entity);
    }
    this.logInvalidation('all', reason);
  }

  async invalidateByAge(entityType: string, maxAgeMs: number): Promise<void> {
    const meta = await versioningService.getEntityVersion(entityType);
    if (!meta) return;
    const age = Date.now() - new Date(meta.last_sync_at).getTime();
    if (age > maxAgeMs) {
      await this.invalidateEntity(entityType, 'TOO_OLD');
    }
  }

  async checkIntegrity(entityType: string): Promise<boolean> {
    const meta = await versioningService.getEntityVersion(entityType);
    const { idbService } = await import('./indexeddb');
    const count = await idbService.count(entityType);
    if (meta && meta.record_count !== count) {
      await this.invalidateEntity(entityType, 'CORRUPTION');
      return false;
    }
    return true;
  }

  /** Cascade rules: categories → products. */
  private async cascadeInvalidation(entityType: string): Promise<void> {
    if (entityType === 'categories') {
      await this.invalidateEntity('products', 'BREAKING_CHANGE');
    }
  }

  private logInvalidation(
    entityType: string,
    reason: InvalidationReason
  ): void {
    if (typeof console !== 'undefined') {
      console.info(
        `[CacheService] Invalidated "${entityType}" — reason: ${reason}`
      );
    }
  }
}

export const cacheService = new CacheService();
