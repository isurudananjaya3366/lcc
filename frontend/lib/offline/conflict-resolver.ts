// ================================================================
// Conflict Resolver — Tasks 63-68
// ================================================================
// Detects and resolves sync conflicts: server-wins, merge,
// stock & price conflict handlers, manual flagging, audit trails.
// ================================================================

import {
  ConflictType,
  ConflictPriority,
  ConflictResolutionStatus,
  ResolutionStrategy,
  PRICE_CHANGE_THRESHOLD_AUTO,
  PRICE_CHANGE_THRESHOLD_MANUAL,
  PRICE_IMPACT_THRESHOLD,
  MANUAL_RESOLUTION_TIMEOUT,
  type Conflict,
  type FieldConflict,
  type ResolutionResult,
  type AuditTrailEntry,
  type ManualResolution,
  type StockMovement,
  type PriceConflictMetadata,
} from './sync-types';

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export class ConflictResolver {
  private conflictDetectedCbs: ((c: Conflict) => void)[] = [];
  private conflictResolvedCbs: ((r: ResolutionResult) => void)[] = [];
  private conflicts: Map<string, Conflict> = new Map();
  private manualResolutions: Map<string, ManualResolution> = new Map();
  private auditTrail: AuditTrailEntry[] = [];

  // ----------------------------------------------------------------
  // Detection
  // ----------------------------------------------------------------

  async detectConflicts(
    localData: Record<string, unknown>[],
    serverData: Record<string, unknown>[]
  ): Promise<Conflict[]> {
    const serverMap = new Map<string, Record<string, unknown>>();
    for (const item of serverData) {
      if (item.id) serverMap.set(item.id as string, item);
    }

    const found: Conflict[] = [];
    for (const local of localData) {
      const id = local.id as string;
      const server = serverMap.get(id);
      if (!server) continue;

      const conflict =
        this.detectStockConflict(local, server) ??
        this.detectPriceConflict(local, server) ??
        this.detectDeleteConflict(local, server) ??
        this.detectUpdateConflict(local, server);

      if (conflict) {
        conflict.priority = this.determinePriority(conflict);
        this.conflicts.set(conflict.id, conflict);
        found.push(conflict);
        for (const cb of this.conflictDetectedCbs) cb(conflict);
      }
    }
    return found;
  }

  private detectUpdateConflict(
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): Conflict | null {
    const localMod = local.updated_at as string | undefined;
    const serverMod = server.updated_at as string | undefined;
    if (!localMod || !serverMod) return null;
    if (localMod === serverMod) return null;
    return this.buildConflict(ConflictType.UPDATE_CONFLICT, local, server);
  }

  private detectDeleteConflict(
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): Conflict | null {
    const localDeleted =
      local.is_deleted === true || local.status === 'deleted';
    const serverDeleted =
      server.is_deleted === true || server.status === 'deleted';
    if (localDeleted !== serverDeleted) {
      return this.buildConflict(ConflictType.DELETE_CONFLICT, local, server);
    }
    return null;
  }

  private detectStockConflict(
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): Conflict | null {
    if (
      typeof local.stock_quantity === 'number' &&
      typeof server.stock_quantity === 'number'
    ) {
      if (local.stock_quantity !== server.stock_quantity) {
        return this.buildConflict(ConflictType.STOCK_CONFLICT, local, server);
      }
    }
    return null;
  }

  private detectPriceConflict(
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): Conflict | null {
    if (typeof local.price === 'number' && typeof server.price === 'number') {
      if (local.price !== server.price) {
        return this.buildConflict(ConflictType.PRICE_CONFLICT, local, server);
      }
    }
    return null;
  }

  private buildConflict(
    type: ConflictType,
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): Conflict {
    return {
      id: generateId(),
      type,
      entityType: (local.entity_type as string) ?? 'unknown',
      entityId: local.id as string,
      localData: local,
      serverData: server,
      localModifiedAt: (local.updated_at as string) ?? new Date().toISOString(),
      serverModifiedAt:
        (server.updated_at as string) ?? new Date().toISOString(),
      detectedAt: new Date().toISOString(),
      priority: ConflictPriority.MEDIUM,
      status: ConflictResolutionStatus.DETECTED,
    };
  }

  private determinePriority(conflict: Conflict): ConflictPriority {
    switch (conflict.type) {
      case ConflictType.STOCK_CONFLICT:
        return ConflictPriority.CRITICAL;
      case ConflictType.PRICE_CONFLICT:
        return ConflictPriority.HIGH;
      case ConflictType.DELETE_CONFLICT:
        return ConflictPriority.HIGH;
      case ConflictType.DATA_INTEGRITY:
        return ConflictPriority.CRITICAL;
      default:
        return ConflictPriority.MEDIUM;
    }
  }

  // ----------------------------------------------------------------
  // Resolution
  // ----------------------------------------------------------------

  async resolveConflict(conflict: Conflict): Promise<ResolutionResult> {
    switch (conflict.type) {
      case ConflictType.STOCK_CONFLICT:
        return this.resolveStockConflict(conflict);
      case ConflictType.PRICE_CONFLICT:
        return this.resolvePriceConflict(conflict);
      default:
        return this.resolveServerWins(conflict);
    }
  }

  async resolveServerWins(conflict: Conflict): Promise<ResolutionResult> {
    const now = new Date().toISOString();
    const result: ResolutionResult = {
      success: true,
      conflictId: conflict.id,
      strategy: ResolutionStrategy.SERVER_WINS,
      resolvedAt: now,
      discardedLocalChanges: conflict.localData,
      appliedServerChanges: conflict.serverData,
      affectedEntities: [conflict.entityId],
      requiresReview: false,
      auditTrail: {
        conflictId: conflict.id,
        resolvedAt: now,
        strategy: ResolutionStrategy.SERVER_WINS,
        entityType: conflict.entityType,
        entityId: conflict.entityId,
        before: conflict.localData,
        after: conflict.serverData,
        discardedFields: this.getChangedFields(
          conflict.localData as Record<string, unknown>,
          conflict.serverData as Record<string, unknown>
        ),
        impact: { transactionsAffected: 0, requiresReview: false },
      },
    };

    conflict.status = ConflictResolutionStatus.RESOLVED;
    conflict.resolutionStrategy = ResolutionStrategy.SERVER_WINS;
    conflict.resolvedAt = now;
    this.storeAuditTrail(result.auditTrail!);
    for (const cb of this.conflictResolvedCbs) cb(result);
    return result;
  }

  async resolveMerge(conflict: Conflict): Promise<ResolutionResult> {
    const local = conflict.localData as Record<string, unknown>;
    const server = conflict.serverData as Record<string, unknown>;
    const fields = this.analyzeFieldLevelConflicts(local, server);
    const merged: Record<string, unknown> = { ...server };

    for (const f of fields) {
      if (f.canAutoMerge && f.mergeStrategy === 'local') {
        merged[f.field] = f.localValue;
      }
    }

    const now = new Date().toISOString();
    const requiresReview = fields.some((f) => !f.canAutoMerge);
    const result: ResolutionResult = {
      success: true,
      conflictId: conflict.id,
      strategy: ResolutionStrategy.MERGE,
      resolvedAt: now,
      discardedLocalChanges: local,
      appliedServerChanges: merged,
      affectedEntities: [conflict.entityId],
      requiresReview,
      auditTrail: {
        conflictId: conflict.id,
        resolvedAt: now,
        strategy: ResolutionStrategy.MERGE,
        entityType: conflict.entityType,
        entityId: conflict.entityId,
        before: local,
        after: merged,
        discardedFields: fields
          .filter((f) => f.mergeStrategy === 'server')
          .map((f) => f.field),
        impact: { transactionsAffected: 0, requiresReview },
      },
    };

    conflict.status = requiresReview
      ? ConflictResolutionStatus.MANUAL
      : ConflictResolutionStatus.RESOLVED;
    conflict.resolutionStrategy = ResolutionStrategy.MERGE;
    conflict.resolvedAt = now;
    this.storeAuditTrail(result.auditTrail!);
    for (const cb of this.conflictResolvedCbs) cb(result);
    return result;
  }

  async resolveStockConflict(conflict: Conflict): Promise<ResolutionResult> {
    const local = conflict.localData as Record<string, unknown>;
    const server = conflict.serverData as Record<string, unknown>;
    const serverStock = (server.stock_quantity as number) ?? 0;
    const localStock = (local.stock_quantity as number) ?? 0;
    const localDelta =
      localStock - ((local._original_stock as number) ?? serverStock);
    const finalStock = Math.max(0, serverStock + localDelta);

    const now = new Date().toISOString();
    const merged = { ...server, stock_quantity: finalStock };
    const result: ResolutionResult = {
      success: true,
      conflictId: conflict.id,
      strategy: ResolutionStrategy.STOCK_CONFLICT_HANDLER,
      resolvedAt: now,
      discardedLocalChanges: local,
      appliedServerChanges: merged,
      affectedEntities: [conflict.entityId],
      requiresReview: finalStock === 0,
      auditTrail: {
        conflictId: conflict.id,
        resolvedAt: now,
        strategy: ResolutionStrategy.STOCK_CONFLICT_HANDLER,
        entityType: conflict.entityType,
        entityId: conflict.entityId,
        before: local,
        after: merged,
        discardedFields: [],
        impact: { transactionsAffected: 0, requiresReview: finalStock === 0 },
      },
    };

    conflict.status = ConflictResolutionStatus.RESOLVED;
    conflict.resolutionStrategy = ResolutionStrategy.STOCK_CONFLICT_HANDLER;
    conflict.resolvedAt = now;
    this.storeAuditTrail(result.auditTrail!);
    for (const cb of this.conflictResolvedCbs) cb(result);
    return result;
  }

  async resolvePriceConflict(conflict: Conflict): Promise<ResolutionResult> {
    const local = conflict.localData as Record<string, unknown>;
    const server = conflict.serverData as Record<string, unknown>;
    const oldPrice = local.price as number;
    const newPrice = server.price as number;
    const percentChange =
      oldPrice > 0 ? Math.abs(newPrice - oldPrice) / oldPrice : 1;

    const threshold = this.determineAutoResolutionThreshold(percentChange);
    if (threshold === 'MANUAL') {
      return this.flagForManualResolution(conflict).then(
        () =>
          ({
            success: true,
            conflictId: conflict.id,
            strategy: ResolutionStrategy.PRICE_CONFLICT_HANDLER,
            resolvedAt: new Date().toISOString(),
            discardedLocalChanges: local,
            appliedServerChanges: server,
            affectedEntities: [conflict.entityId],
            requiresReview: true,
          }) as ResolutionResult
      );
    }

    // Auto-accept: server price wins
    const now = new Date().toISOString();
    const result: ResolutionResult = {
      success: true,
      conflictId: conflict.id,
      strategy: ResolutionStrategy.PRICE_CONFLICT_HANDLER,
      resolvedAt: now,
      discardedLocalChanges: local,
      appliedServerChanges: server,
      affectedEntities: [conflict.entityId],
      requiresReview: threshold === 'FLAG',
      auditTrail: {
        conflictId: conflict.id,
        resolvedAt: now,
        strategy: ResolutionStrategy.PRICE_CONFLICT_HANDLER,
        entityType: conflict.entityType,
        entityId: conflict.entityId,
        before: local,
        after: server,
        discardedFields: ['price'],
        impact: {
          transactionsAffected: 0,
          requiresReview: threshold === 'FLAG',
        },
      },
    };

    conflict.status = ConflictResolutionStatus.RESOLVED;
    conflict.resolutionStrategy = ResolutionStrategy.PRICE_CONFLICT_HANDLER;
    conflict.resolvedAt = now;
    this.storeAuditTrail(result.auditTrail!);
    for (const cb of this.conflictResolvedCbs) cb(result);
    return result;
  }

  private determineAutoResolutionThreshold(
    percentChange: number
  ): 'AUTO' | 'FLAG' | 'MANUAL' {
    if (percentChange <= PRICE_CHANGE_THRESHOLD_AUTO) return 'AUTO';
    if (percentChange <= PRICE_CHANGE_THRESHOLD_MANUAL) return 'FLAG';
    return 'MANUAL';
  }

  // ----------------------------------------------------------------
  // Manual Resolution
  // ----------------------------------------------------------------

  async flagForManualResolution(conflict: Conflict): Promise<ManualResolution> {
    const manual: ManualResolution = {
      id: generateId(),
      conflictId: conflict.id,
      priority: conflict.priority,
      entityType: conflict.entityType,
      entityId: conflict.entityId,
      conflictType: conflict.type,
      localData: conflict.localData,
      serverData: conflict.serverData,
      suggestedResolution:
        'Review both versions and decide which data to keep.',
      status: 'PENDING',
      createdAt: new Date().toISOString(),
      dueBy: new Date(Date.now() + MANUAL_RESOLUTION_TIMEOUT).toISOString(),
    };
    this.manualResolutions.set(manual.id, manual);
    conflict.status = ConflictResolutionStatus.MANUAL;
    return manual;
  }

  async getManualResolutions(): Promise<ManualResolution[]> {
    return Array.from(this.manualResolutions.values());
  }

  async resolveManually(
    manualResolutionId: string,
    resolution: string
  ): Promise<void> {
    const mr = this.manualResolutions.get(manualResolutionId);
    if (!mr)
      throw new Error(`Manual resolution ${manualResolutionId} not found`);
    mr.status = 'RESOLVED';
    mr.resolution = resolution;
    mr.resolvedAt = new Date().toISOString();

    const conflict = this.conflicts.get(mr.conflictId);
    if (conflict) {
      conflict.status = ConflictResolutionStatus.RESOLVED;
      conflict.resolvedAt = mr.resolvedAt;
    }
  }

  // ----------------------------------------------------------------
  // Field Analysis
  // ----------------------------------------------------------------

  private analyzeFieldLevelConflicts(
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): FieldConflict[] {
    const allKeys = new Set([...Object.keys(local), ...Object.keys(server)]);
    const results: FieldConflict[] = [];
    const skipFields = new Set(['id', 'created_at', 'updated_at']);

    for (const key of allKeys) {
      if (skipFields.has(key)) continue;
      const lv = local[key];
      const sv = server[key];
      if (JSON.stringify(lv) !== JSON.stringify(sv)) {
        const onlyLocal = sv === undefined;
        const onlyServer = lv === undefined;
        results.push({
          field: key,
          localValue: lv,
          serverValue: sv,
          canAutoMerge: onlyLocal || onlyServer,
          mergeStrategy: onlyLocal ? 'local' : onlyServer ? 'server' : 'manual',
        });
      }
    }
    return results;
  }

  private getChangedFields(
    local: Record<string, unknown>,
    server: Record<string, unknown>
  ): string[] {
    return Object.keys(local).filter(
      (k) => JSON.stringify(local[k]) !== JSON.stringify(server[k])
    );
  }

  // ----------------------------------------------------------------
  // Audit & Events
  // ----------------------------------------------------------------

  private storeAuditTrail(entry: AuditTrailEntry): void {
    this.auditTrail.push(entry);
  }

  getAuditTrail(): AuditTrailEntry[] {
    return [...this.auditTrail];
  }

  onConflictDetected(callback: (c: Conflict) => void): () => void {
    this.conflictDetectedCbs.push(callback);
    return () => {
      this.conflictDetectedCbs = this.conflictDetectedCbs.filter(
        (cb) => cb !== callback
      );
    };
  }

  onConflictResolved(callback: (r: ResolutionResult) => void): () => void {
    this.conflictResolvedCbs.push(callback);
    return () => {
      this.conflictResolvedCbs = this.conflictResolvedCbs.filter(
        (cb) => cb !== callback
      );
    };
  }
}

export const conflictResolver = new ConflictResolver();
