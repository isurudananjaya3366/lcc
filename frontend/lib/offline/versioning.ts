// ================================================================
// Data Versioning Service — Task 25
// ================================================================
// Tracks per-entity sync versions, timestamps, and staleness
// using the sync_meta object store.
// ================================================================

import { idbService } from './indexeddb';
import { ObjectStoreNames, type SyncMeta } from './schema';

const STORE = ObjectStoreNames.SYNC_META;

// ── Types ──────────────────────────────────────────────────────

export interface VersionInfo {
  entity_type: string;
  version?: string;
  last_sync_at: string;
  record_count: number;
  sync_token?: string;
  has_more: boolean;
  etag?: string;
  error_count: number;
  last_error?: string;
}

export type VersionComparison =
  | 'equal'
  | 'local_newer'
  | 'server_newer'
  | 'unknown';

// ── Service ────────────────────────────────────────────────────

class VersioningService {
  async getEntityVersion(entityType: string): Promise<SyncMeta | undefined> {
    return idbService.get<SyncMeta>(STORE, entityType);
  }

  async setEntityVersion(
    entityType: string,
    info: Partial<VersionInfo>
  ): Promise<void> {
    const existing = await this.getEntityVersion(entityType);
    const meta: SyncMeta = {
      entity_type: entityType,
      last_sync_at: info.last_sync_at ?? new Date().toISOString(),
      version: info.version ?? existing?.version,
      record_count: info.record_count ?? existing?.record_count ?? 0,
      sync_token: info.sync_token ?? existing?.sync_token,
      has_more: info.has_more ?? false,
      etag: info.etag ?? existing?.etag,
      error_count: info.error_count ?? existing?.error_count ?? 0,
      last_error: info.last_error ?? existing?.last_error,
    };
    await idbService.put(STORE, meta);
  }

  compareVersions(
    localVersion: string | undefined,
    serverVersion: string
  ): VersionComparison {
    if (!localVersion) return 'server_newer';
    if (localVersion === serverVersion) return 'equal';
    return localVersion < serverVersion ? 'server_newer' : 'local_newer';
  }

  /** Returns true if the entity hasn't been synced within `thresholdMs` milliseconds. */
  async isStale(entityType: string, thresholdMs: number): Promise<boolean> {
    const meta = await this.getEntityVersion(entityType);
    if (!meta) return true;
    const elapsed = Date.now() - new Date(meta.last_sync_at).getTime();
    return elapsed > thresholdMs;
  }

  async bulkUpdateVersions(
    versions: Map<string, Partial<VersionInfo>>
  ): Promise<void> {
    for (const [entityType, info] of versions) {
      await this.setEntityVersion(entityType, info);
    }
  }

  async resetEntityVersion(entityType: string): Promise<void> {
    await idbService.delete(STORE, entityType);
  }

  async getAllVersions(): Promise<SyncMeta[]> {
    return idbService.getAll<SyncMeta>(STORE);
  }
}

export const versioningService = new VersioningService();
