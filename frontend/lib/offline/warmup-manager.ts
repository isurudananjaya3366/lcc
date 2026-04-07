// ================================================================
// Cache Warmup Manager — Task 34
// ================================================================
// Orchestrates tiered warmup of the local cache after login.
// Critical data loads first; background tiers follow.
// ================================================================

import { cacheService, type SyncProgress } from './cache-service';
import { versioningService } from './versioning';

// ── Types ──────────────────────────────────────────────────────

export interface WarmupTierStatus {
  tier: number;
  name: string;
  status: 'pending' | 'in-progress' | 'completed' | 'failed';
  items_total: number;
  items_completed: number;
  errors: string[];
}

export interface WarmupProgress {
  status: 'not-started' | 'in-progress' | 'completed' | 'failed';
  current_tier: number;
  tiers: WarmupTierStatus[];
  overall_progress: number; // 0-100
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
}

type WarmupCallback = (progress: WarmupProgress) => void;

// ── Tier definitions ───────────────────────────────────────────

const TIERS: { tier: number; name: string; blocking: boolean }[] = [
  { tier: 1, name: 'Terminal Settings', blocking: true },
  { tier: 2, name: 'Products & Categories', blocking: true },
  { tier: 3, name: 'Customers', blocking: false },
  { tier: 4, name: 'Media Assets', blocking: false },
];

// ── Manager ────────────────────────────────────────────────────

class WarmupManager {
  private cancelled = false;

  async startWarmup(
    _terminalId: string,
    onProgress?: WarmupCallback
  ): Promise<WarmupProgress> {
    this.cancelled = false;

    const progress: WarmupProgress = {
      status: 'in-progress',
      current_tier: 1,
      tiers: TIERS.map((t) => ({
        tier: t.tier,
        name: t.name,
        status: 'pending' as const,
        items_total: 0,
        items_completed: 0,
        errors: [],
      })),
      overall_progress: 0,
      started_at: new Date().toISOString(),
    };

    const emit = () =>
      onProgress?.({
        ...progress,
        tiers: progress.tiers.map((t) => ({ ...t })),
      });
    emit();

    try {
      // Tier 1 — Settings (blocking)
      await this.runTier(progress, 0, () =>
        cacheService.syncSettings(this.tierProgressFor(progress, 0, emit))
      );
      if (this.cancelled) return this.cancel(progress);

      // Tier 2 — Products + Categories (blocking)
      await this.runTier(progress, 1, async () => {
        await cacheService.syncCategories(
          'full',
          this.tierProgressFor(progress, 1, emit)
        );
        await cacheService.syncProducts(
          'full',
          this.tierProgressFor(progress, 1, emit)
        );
      });
      if (this.cancelled) return this.cancel(progress);

      // Tier 3 — Customers (background)
      await this.runTier(progress, 2, () =>
        cacheService.syncCustomers(
          'full',
          this.tierProgressFor(progress, 2, emit)
        )
      );
      if (this.cancelled) return this.cancel(progress);

      // Tier 4 — Media (no-op for now; images cached via SW)
      progress.tiers[3]!.status = 'completed';

      progress.status = 'completed';
      progress.overall_progress = 100;
      progress.completed_at = new Date().toISOString();
      progress.duration_ms =
        new Date(progress.completed_at).getTime() -
        new Date(progress.started_at!).getTime();
      emit();
      return progress;
    } catch (error) {
      progress.status = 'failed';
      emit();
      throw error;
    }
  }

  cancelWarmup(): void {
    this.cancelled = true;
  }

  async shouldPerformFullWarmup(): Promise<boolean> {
    // Check versioning metadata — if we have recent sync metadata for
    // core entities then an incremental warmup suffices.
    try {
      const versions = await versioningService.getAllVersions();
      if (versions.length === 0) return true; // first login

      // If any critical entity is stale (>4 hours), full warmup needed
      const STALE_THRESHOLD_MS = 4 * 60 * 60 * 1000;
      for (const v of versions) {
        if (!v.last_sync_at) return true;
        const age = Date.now() - new Date(v.last_sync_at).getTime();
        if (age > STALE_THRESHOLD_MS) return true;
      }
      return false;
    } catch {
      return true; // err on the side of full warmup
    }
  }

  // ── Helpers ──────────────────────────────────────────────────

  private async runTier(
    progress: WarmupProgress,
    tierIndex: number,
    fn: () => Promise<void>
  ): Promise<void> {
    const tier = progress.tiers[tierIndex]!;
    progress.current_tier = tier.tier;
    tier.status = 'in-progress';
    try {
      await fn();
      tier.status = 'completed';
    } catch (error) {
      tier.status = 'failed';
      tier.errors.push(String(error));
      throw error;
    }
    progress.overall_progress = Math.round(
      (progress.tiers.filter((t) => t.status === 'completed').length /
        progress.tiers.length) *
        100
    );
  }

  private tierProgressFor(
    progress: WarmupProgress,
    tierIndex: number,
    emit: () => void
  ): (sp: SyncProgress) => void {
    return (sp) => {
      const tier = progress.tiers[tierIndex]!;
      tier.items_total = sp.total;
      tier.items_completed = sp.loaded;
      emit();
    };
  }

  private cancel(progress: WarmupProgress): WarmupProgress {
    progress.status = 'failed';
    return progress;
  }
}

export const warmupManager = new WarmupManager();
