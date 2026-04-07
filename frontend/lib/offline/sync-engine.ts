// ================================================================
// Sync Engine — Tasks 53-62, 69-72
// ================================================================
// Main sync orchestration: push transactions, pull updates,
// auto-sync on reconnect, batch processing, progress tracking,
// error handling with exponential backoff, and callbacks.
// ================================================================

import {
  SyncStatus,
  SyncPhase,
  SyncType,
  ErrorCategory,
  ErrorSeverity,
  DEFAULT_BATCH_SIZE,
  MAX_BATCH_SIZE,
  SYNC_LOCK_TIMEOUT,
  PUSH_ENDPOINT,
  PULL_ENDPOINT,
  DELTA_SYNC_STORAGE_KEY,
  type SyncEngineConfig,
  type SyncProgress,
  type SyncResult,
  type SyncContext,
  type SyncErrorInfo,
  type BackoffConfig,
  type Batch,
  type BatchResult,
  type ServerUpdates,
  type CallbackOptions,
  type CallbackFilter,
  type DeltaSyncState,
  type DeltaSyncHeaders,
  DEFAULT_SYNC_ENGINE_CONFIG,
  DEFAULT_BACKOFF_CONFIG,
} from './sync-types';

import { ConnectionMonitor } from './connection-monitor';
import type { Product, Customer } from './schema';
import { ConflictResolver } from './conflict-resolver';
import { SyncAnalytics } from './sync-analytics';

// ----------------------------------------------------------------
// Backoff Strategy
// ----------------------------------------------------------------

export class BackoffStrategy {
  private config: BackoffConfig;
  private currentAttempt = 0;

  constructor(config?: Partial<BackoffConfig>) {
    this.config = { ...DEFAULT_BACKOFF_CONFIG, ...config };
  }

  shouldRetry(): boolean {
    return this.currentAttempt < this.config.maxAttempts;
  }

  getNextDelay(): number {
    const base =
      this.config.initialDelay *
      Math.pow(this.config.multiplier, this.currentAttempt);
    const capped = Math.min(base, this.config.maxDelay);
    const jitter = capped * this.config.jitterFactor * Math.random();
    this.currentAttempt++;
    return capped + jitter;
  }

  async wait(): Promise<void> {
    const delay = this.getNextDelay();
    await new Promise((r) => setTimeout(r, delay));
  }

  reset(): void {
    this.currentAttempt = 0;
  }

  getCurrentAttempt(): number {
    return this.currentAttempt;
  }

  getMaxAttempts(): number {
    return this.config.maxAttempts;
  }
}

// ----------------------------------------------------------------
// SyncError
// ----------------------------------------------------------------

export class SyncError extends Error {
  code: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  retryable: boolean;
  httpStatus?: number;
  originalError?: Error;

  constructor(params: {
    code: string;
    message: string;
    category: ErrorCategory;
    severity: ErrorSeverity;
    retryable: boolean;
    httpStatus?: number;
    originalError?: Error;
  }) {
    super(params.message);
    this.name = 'SyncError';
    this.code = params.code;
    this.category = params.category;
    this.severity = params.severity;
    this.retryable = params.retryable;
    this.httpStatus = params.httpStatus;
    this.originalError = params.originalError;
  }

  toJSON(): SyncErrorInfo {
    return {
      code: this.code,
      message: this.message,
      category: this.category,
      severity: this.severity,
      retryable: this.retryable,
    };
  }
}

// ----------------------------------------------------------------
// Callback registration helpers
// ----------------------------------------------------------------

interface RegisteredCallback {
  callback: (result: SyncResult, context: SyncContext) => void | Promise<void>;
  options: CallbackOptions;
}

// ----------------------------------------------------------------
// SyncEngine
// ----------------------------------------------------------------

export class SyncEngine {
  private static instance: SyncEngine | null = null;

  private config: SyncEngineConfig;
  private currentStatus: SyncStatus = SyncStatus.IDLE;
  private lastSyncTime = 0;
  private syncLock = false;
  private syncLockTimestamp = 0;
  private autoSyncTimer?: ReturnType<typeof setInterval>;
  private connectionMonitor: ConnectionMonitor;
  private conflictResolver: ConflictResolver;
  private analytics: SyncAnalytics;
  private backoff: BackoffStrategy;

  // Event listeners
  private statusListeners: ((status: SyncStatus) => void)[] = [];
  private progressListeners: ((p: SyncProgress) => void)[] = [];
  private completionCallbacks: RegisteredCallback[] = [];
  private errorListeners: ((e: SyncErrorInfo) => void)[] = [];

  // Delta sync state (Task 61)
  private deltaSyncState: DeltaSyncState = {
    lastSyncTimestamp: null,
    entityETags: {},
    syncToken: null,
    watermarks: {},
  };

  private destroyed = false;

  private constructor(config: SyncEngineConfig) {
    this.config = config;
    this.connectionMonitor = new ConnectionMonitor();
    this.conflictResolver = new ConflictResolver();
    this.analytics = new SyncAnalytics();
    this.backoff = new BackoffStrategy({
      maxAttempts: config.maxRetryAttempts,
    });
  }

  // ---- Singleton ----

  static getInstance(): SyncEngine {
    if (!SyncEngine.instance) {
      SyncEngine.instance = new SyncEngine(DEFAULT_SYNC_ENGINE_CONFIG);
    }
    return SyncEngine.instance;
  }

  static initialize(config: Partial<SyncEngineConfig> = {}): SyncEngine {
    SyncEngine.instance = new SyncEngine({
      ...DEFAULT_SYNC_ENGINE_CONFIG,
      ...config,
    });
    return SyncEngine.instance;
  }

  // ---- Lifecycle ----

  async init(): Promise<boolean> {
    this.loadDeltaSyncState();
    this.setupConnectionMonitoring();
    if (this.config.autoSyncEnabled) this.setupAutoSyncTimer();
    return true;
  }

  async destroy(): Promise<void> {
    this.destroyed = true;
    this.saveDeltaSyncState();
    this.clearAutoSyncTimer();
    this.connectionMonitor.destroy();
    this.releaseSyncLock();
    this.statusListeners = [];
    this.progressListeners = [];
    this.completionCallbacks = [];
    this.errorListeners = [];
    SyncEngine.instance = null;
  }

  // ---- Status ----

  getCurrentStatus(): SyncStatus {
    return this.currentStatus;
  }

  getIsOnline(): boolean {
    return this.connectionMonitor.getIsOnline();
  }

  isSyncing(): boolean {
    return (
      this.currentStatus === SyncStatus.PUSHING ||
      this.currentStatus === SyncStatus.PULLING ||
      this.currentStatus === SyncStatus.RESOLVING_CONFLICTS
    );
  }

  getLastSyncTime(): number {
    return this.lastSyncTime;
  }

  isSyncLocked(): boolean {
    // Auto-expire stale locks
    if (
      this.syncLock &&
      Date.now() - this.syncLockTimestamp > SYNC_LOCK_TIMEOUT
    ) {
      this.releaseSyncLock();
    }
    return this.syncLock;
  }

  // ---- Sync Operations ----

  async startSync(type: SyncType = SyncType.FULL): Promise<SyncResult> {
    if (this.destroyed)
      throw new SyncError({
        code: 'DESTROYED',
        message: 'Engine destroyed',
        category: ErrorCategory.DATA_ERROR,
        severity: ErrorSeverity.FATAL,
        retryable: false,
      });
    if (this.isSyncing())
      throw new SyncError({
        code: 'SYNC_IN_PROGRESS',
        message: 'Sync already in progress',
        category: ErrorCategory.DATA_ERROR,
        severity: ErrorSeverity.WARNING,
        retryable: false,
      });

    if (!this.acquireSyncLock()) {
      throw new SyncError({
        code: 'LOCK_FAILED',
        message: 'Could not acquire sync lock',
        category: ErrorCategory.DATA_ERROR,
        severity: ErrorSeverity.ERROR,
        retryable: true,
      });
    }

    const syncId = `sync-${Date.now()}`;
    const startTime = new Date().toISOString();
    await this.analytics.trackSyncStart(syncId);

    const context: SyncContext = {
      terminalId: 'terminal-1',
      syncId,
      triggeredBy: 'manual',
      affectedEntities: [],
    };

    try {
      this.setStatus(SyncStatus.CONNECTING);
      const online = await this.connectionMonitor.checkConnection();
      if (!online) {
        throw new SyncError({
          code: 'OFFLINE',
          message: 'No connection',
          category: ErrorCategory.NETWORK_ERROR,
          severity: ErrorSeverity.ERROR,
          retryable: true,
        });
      }

      let result: SyncResult;
      if (type === SyncType.PUSH) {
        result = await this.pushTransactions(syncId, startTime);
      } else if (type === SyncType.PULL) {
        result = await this.pullUpdates(syncId, startTime);
      } else {
        result = await this.fullSync(syncId, startTime);
      }

      this.lastSyncTime = Date.now();
      this.backoff.reset();
      this.setStatus(SyncStatus.COMPLETED);

      await this.analytics.trackSyncComplete(syncId, result, context);
      this.notifyCompletion(result, context);
      return result;
    } catch (err) {
      this.setStatus(SyncStatus.ERROR);
      const syncError =
        err instanceof SyncError
          ? err
          : new SyncError({
              code: 'UNKNOWN',
              message: (err as Error).message,
              category: ErrorCategory.UNKNOWN_ERROR,
              severity: ErrorSeverity.ERROR,
              retryable: true,
              originalError: err as Error,
            });
      for (const l of this.errorListeners) l(syncError.toJSON());

      const failResult = this.buildEmptyResult(type, startTime, false, [
        syncError.toJSON(),
      ]);
      await this.analytics.trackSyncComplete(syncId, failResult, context);
      return failResult;
    } finally {
      this.releaseSyncLock();
    }
  }

  async manualSync(): Promise<SyncResult> {
    return this.startSync(SyncType.FULL);
  }

  // ---- Push ----

  private async pushTransactions(
    syncId: string,
    startTime: string
  ): Promise<SyncResult> {
    this.setStatus(SyncStatus.PUSHING);
    this.emitProgress(SyncPhase.PUSHING, 'Preparing transactions...', 0, 0, 0);

    // Fetch pending transactions from the queue (via IndexedDB)
    const { transactionsService } = await import('./stores/transactions');
    const pending = await transactionsService.getPendingTransactions();

    if (pending.length === 0) {
      return this.buildEmptyResult(SyncType.PUSH, startTime, true);
    }

    const batches = this.createBatches(pending);
    let pushed = 0;
    let failed = 0;
    const errors: SyncErrorInfo[] = [];

    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i]!;
      this.emitProgress(
        SyncPhase.PUSHING,
        `Pushing batch ${i + 1} of ${batches.length}`,
        ((i + 1) / batches.length) * 100,
        i + 1,
        batches.length
      );

      const result = await this.processBatch(batch);
      pushed += result.successful.length;
      failed += result.failed.length;

      // Mark synced/failed in local store
      for (const s of result.successful) {
        await transactionsService.markTransactionSynced(s.id, s.serverId);
      }
      for (const f of result.failed) {
        await transactionsService.markTransactionFailed(f.id, f.error);
      }

      if (result.failed.length > 0 && !result.success) {
        errors.push({
          code: 'BATCH_PARTIAL_FAILURE',
          message: `Batch ${i + 1} had ${result.failed.length} failures`,
          category: ErrorCategory.SERVER_ERROR,
          severity: ErrorSeverity.WARNING,
          retryable: true,
        });
      }
    }

    const endTime = new Date().toISOString();
    return {
      success: failed === 0,
      syncType: SyncType.PUSH,
      duration: new Date(endTime).getTime() - new Date(startTime).getTime(),
      startTime,
      endTime,
      stats: {
        transactionsPushed: pushed,
        transactionsFailed: failed,
        entitiesPulled: 0,
        conflictsDetected: 0,
        conflictsResolved: 0,
        conflictsManual: 0,
      },
      errors,
      warnings: [],
    };
  }

  private createBatches(transactions: unknown[]): Batch[] {
    const size = Math.min(this.config.batchSize, MAX_BATCH_SIZE);
    const batches: Batch[] = [];
    for (let i = 0; i < transactions.length; i += size) {
      const slice = transactions.slice(i, i + size);
      batches.push({
        index: batches.length,
        transactions: slice as Batch['transactions'],
        size: slice.length,
        estimatedSize: JSON.stringify(slice).length,
        timeout: this.config.pushTimeout,
      });
    }
    return batches;
  }

  private async processBatch(batch: Batch): Promise<BatchResult> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), batch.timeout);
    try {
      const res = await fetch(`${this.config.apiEndpoint}${PUSH_ENDPOINT}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transactions: batch.transactions }),
        signal: controller.signal,
      });
      clearTimeout(timer);
      if (!res.ok) {
        throw new SyncError({
          code: `HTTP_${res.status}`,
          message: res.statusText,
          category: this.categorizeHttpError(res.status),
          severity: ErrorSeverity.ERROR,
          retryable: res.status >= 500,
          httpStatus: res.status,
        });
      }
      return (await res.json()) as BatchResult;
    } catch (err) {
      clearTimeout(timer);
      if (err instanceof SyncError) throw err;
      throw new SyncError({
        code: 'PUSH_FAILED',
        message: (err as Error).message,
        category: ErrorCategory.NETWORK_ERROR,
        severity: ErrorSeverity.ERROR,
        retryable: true,
        originalError: err as Error,
      });
    }
  }

  // ---- Pull ----

  private async pullUpdates(
    syncId: string,
    startTime: string
  ): Promise<SyncResult> {
    this.setStatus(SyncStatus.PULLING);
    this.emitProgress(SyncPhase.PULLING, 'Pulling server updates...', 0, 0, -1);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.config.pullTimeout);
    let entitiesPulled = 0;
    let conflictsDetected = 0;
    let conflictsResolved = 0;
    let conflictsManual = 0;
    const errors: SyncErrorInfo[] = [];

    try {
      // Build delta sync headers (Task 61)
      const deltaHeaders = this.buildDeltaSyncHeaders();

      const res = await fetch(`${this.config.apiEndpoint}${PULL_ENDPOINT}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', ...deltaHeaders },
        signal: controller.signal,
      });
      clearTimeout(timer);

      // Handle 304 Not Modified — no changes since last sync (Task 61)
      if (res.status === 304) {
        this.lastSyncTime = Date.now();
        this.deltaSyncState.lastSyncTimestamp = new Date().toISOString();
        this.saveDeltaSyncState();
        return {
          success: true,
          syncType: SyncType.PULL,
          duration: Date.now() - new Date(startTime).getTime(),
          startTime,
          endTime: new Date().toISOString(),
          stats: {
            transactionsPushed: 0,
            transactionsFailed: 0,
            entitiesPulled: 0,
            conflictsDetected: 0,
            conflictsResolved: 0,
            conflictsManual: 0,
          },
          errors: [],
          warnings: ['No changes since last sync (304 Not Modified)'],
        };
      }

      // Handle 410 Gone — sync token expired, require full sync
      if (res.status === 410) {
        this.deltaSyncState.syncToken = null;
        this.deltaSyncState.entityETags = {};
        this.saveDeltaSyncState();
        throw new SyncError({
          code: 'SYNC_TOKEN_EXPIRED',
          message: 'Sync token expired — full sync required',
          category: ErrorCategory.DATA_ERROR,
          severity: ErrorSeverity.WARNING,
          retryable: true,
        });
      }

      if (!res.ok) {
        throw new SyncError({
          code: `HTTP_${res.status}`,
          message: res.statusText,
          category: this.categorizeHttpError(res.status),
          severity: ErrorSeverity.ERROR,
          retryable: res.status >= 500,
          httpStatus: res.status,
        });
      }

      // Store delta sync metadata from response headers (Task 61)
      this.updateDeltaSyncFromResponse(res);

      const updates = (await res.json()) as ServerUpdates;
      entitiesPulled = this.countEntities(updates);

      // Conflict detection & resolution
      if (updates.products?.updated?.length) {
        this.setStatus(SyncStatus.RESOLVING_CONFLICTS);
        const { productsService } = await import('./stores/products');
        const localProducts = await productsService.getAllProducts();
        const conflicts = await this.conflictResolver.detectConflicts(
          localProducts as unknown as Record<string, unknown>[],
          updates.products.updated as Record<string, unknown>[]
        );
        conflictsDetected += conflicts.length;
        for (const c of conflicts) {
          const result = await this.conflictResolver.resolveConflict(c);
          if (result.requiresReview) conflictsManual++;
          else conflictsResolved++;
        }
      }

      await this.applyUpdates(updates);

      // Update delta sync timestamp on success (Task 61)
      this.deltaSyncState.lastSyncTimestamp = new Date().toISOString();
      this.saveDeltaSyncState();
    } catch (err) {
      clearTimeout(timer);
      const syncError =
        err instanceof SyncError
          ? err
          : new SyncError({
              code: 'PULL_FAILED',
              message: (err as Error).message,
              category: ErrorCategory.NETWORK_ERROR,
              severity: ErrorSeverity.ERROR,
              retryable: true,
              originalError: err as Error,
            });
      errors.push(syncError.toJSON());
    }

    const endTime = new Date().toISOString();
    return {
      success: errors.length === 0,
      syncType: SyncType.PULL,
      duration: new Date(endTime).getTime() - new Date(startTime).getTime(),
      startTime,
      endTime,
      stats: {
        transactionsPushed: 0,
        transactionsFailed: 0,
        entitiesPulled,
        conflictsDetected,
        conflictsResolved,
        conflictsManual,
      },
      errors,
      warnings: [],
    };
  }

  private async applyUpdates(updates: ServerUpdates): Promise<void> {
    if (updates.products) {
      const { productsService } = await import('./stores/products');
      for (const p of updates.products.created ?? [])
        await productsService.addProduct(p as Product);
      for (const p of updates.products.updated ?? [])
        await productsService.updateProduct(
          (p as { id: string }).id,
          p as Partial<Product>
        );
      for (const id of updates.products.deleted ?? [])
        await productsService.deleteProduct(id);
    }
    if (updates.customers) {
      const { customersService } = await import('./stores/customers');
      for (const c of updates.customers.created ?? [])
        await customersService.addCustomer(c as Customer);
      for (const c of updates.customers.updated ?? [])
        await customersService.updateCustomer(
          (c as { id: string }).id,
          c as Partial<Customer>
        );
      for (const id of updates.customers.deleted ?? [])
        await customersService.deleteCustomer(id);
    }
  }

  private countEntities(updates: ServerUpdates): number {
    let count = 0;
    for (const key of Object.keys(updates) as (keyof ServerUpdates)[]) {
      const entity = updates[key];
      if (entity) {
        count +=
          (entity.created?.length ?? 0) +
          (entity.updated?.length ?? 0) +
          (entity.deleted?.length ?? 0);
      }
    }
    return count;
  }

  // ---- Delta Sync Helpers (Task 61) ----

  private buildDeltaSyncHeaders(): Record<string, string> {
    const headers: Record<string, string> = {};

    // If-Modified-Since: use last sync timestamp in RFC 7231 format
    if (this.deltaSyncState.lastSyncTimestamp) {
      const date = new Date(this.deltaSyncState.lastSyncTimestamp);
      headers['If-Modified-Since'] = date.toUTCString();
    }

    // If-None-Match: combine entity ETags
    const etagEntries = Object.entries(this.deltaSyncState.entityETags);
    if (etagEntries.length > 0) {
      headers['If-None-Match'] = etagEntries.map(([, etag]) => etag).join(', ');
    }

    // X-Sync-Token: continuation token for paginated sync
    if (this.deltaSyncState.syncToken) {
      headers['X-Sync-Token'] = this.deltaSyncState.syncToken;
    }

    return headers;
  }

  private updateDeltaSyncFromResponse(res: Response): void {
    // Store ETag from response
    const etag = res.headers.get('ETag');
    if (etag) {
      this.deltaSyncState.entityETags['_all'] = etag;
    }

    // Store per-entity ETags if returned via custom headers
    const entityEtags = res.headers.get('X-Entity-ETags');
    if (entityEtags) {
      for (const pair of entityEtags.split(',')) {
        const [key, value] = pair.split('=');
        if (key && value) {
          this.deltaSyncState.entityETags[key.trim()] = value.trim();
        }
      }
    }

    // Store sync token for next request
    const syncToken = res.headers.get('X-Sync-Token');
    if (syncToken) {
      this.deltaSyncState.syncToken = syncToken;
    }

    // Update last modified from server
    const lastModified = res.headers.get('Last-Modified');
    if (lastModified) {
      this.deltaSyncState.lastSyncTimestamp = new Date(
        lastModified
      ).toISOString();
    }
  }

  private loadDeltaSyncState(): void {
    try {
      const stored = localStorage.getItem(DELTA_SYNC_STORAGE_KEY);
      if (stored) {
        this.deltaSyncState = JSON.parse(stored) as DeltaSyncState;
      }
    } catch {
      // Use default state if localStorage data is corrupted
    }
  }

  private saveDeltaSyncState(): void {
    try {
      localStorage.setItem(
        DELTA_SYNC_STORAGE_KEY,
        JSON.stringify(this.deltaSyncState)
      );
    } catch {
      // Silently fail — localStorage may be full or disabled
    }
  }

  getDeltaSyncState(): DeltaSyncState {
    return { ...this.deltaSyncState };
  }

  resetDeltaSyncState(): void {
    this.deltaSyncState = {
      lastSyncTimestamp: null,
      entityETags: {},
      syncToken: null,
      watermarks: {},
    };
    this.saveDeltaSyncState();
  }

  // ---- Full Sync ----

  private async fullSync(
    syncId: string,
    startTime: string
  ): Promise<SyncResult> {
    const pushResult = await this.pushTransactions(syncId, startTime);
    const pullStart = new Date().toISOString();
    const pullResult = await this.pullUpdates(syncId, pullStart);

    const endTime = new Date().toISOString();
    return {
      success: pushResult.success && pullResult.success,
      syncType: SyncType.FULL,
      duration: new Date(endTime).getTime() - new Date(startTime).getTime(),
      startTime,
      endTime,
      stats: {
        transactionsPushed: pushResult.stats.transactionsPushed,
        transactionsFailed: pushResult.stats.transactionsFailed,
        entitiesPulled: pullResult.stats.entitiesPulled,
        conflictsDetected: pullResult.stats.conflictsDetected,
        conflictsResolved: pullResult.stats.conflictsResolved,
        conflictsManual: pullResult.stats.conflictsManual,
      },
      errors: [...pushResult.errors, ...pullResult.errors],
      warnings: [...pushResult.warnings, ...pullResult.warnings],
    };
  }

  // ---- Lock Management ----

  private acquireSyncLock(): boolean {
    if (this.isSyncLocked()) return false;
    this.syncLock = true;
    this.syncLockTimestamp = Date.now();
    return true;
  }

  private releaseSyncLock(): void {
    this.syncLock = false;
    this.syncLockTimestamp = 0;
  }

  // ---- Auto-Sync ----

  private setupAutoSyncTimer(): void {
    this.autoSyncTimer = setInterval(() => {
      if (this.connectionMonitor.getIsOnline() && !this.isSyncing()) {
        this.startSync(SyncType.FULL).catch(() => {});
      }
    }, this.config.syncInterval);
  }

  private clearAutoSyncTimer(): void {
    if (this.autoSyncTimer) {
      clearInterval(this.autoSyncTimer);
      this.autoSyncTimer = undefined;
    }
  }

  private setupConnectionMonitoring(): void {
    this.connectionMonitor.onConnectionChange((event) => {
      if (
        event.online &&
        !event.previouslyOnline &&
        this.config.autoSyncEnabled
      ) {
        // Reconnected — trigger sync
        this.startSync(SyncType.FULL).catch(() => {});
      }
    });
    this.connectionMonitor.startMonitoring();
  }

  // ---- Status & Progress ----

  private setStatus(status: SyncStatus): void {
    this.currentStatus = status;
    for (const l of this.statusListeners) l(status);
  }

  private emitProgress(
    phase: SyncPhase,
    desc: string,
    pct: number,
    current: number,
    total: number
  ): void {
    const p: SyncProgress = {
      phase,
      phaseDescription: desc,
      percentage: pct,
      current,
      total,
      currentOperation: desc,
      startTime: new Date().toISOString(),
      elapsedTime: 0,
    };
    for (const l of this.progressListeners) l(p);
  }

  // ---- Event Subscriptions ----

  onStatusChange(callback: (status: SyncStatus) => void): () => void {
    this.statusListeners.push(callback);
    return () => {
      this.statusListeners = this.statusListeners.filter((c) => c !== callback);
    };
  }

  onProgress(callback: (p: SyncProgress) => void): () => void {
    this.progressListeners.push(callback);
    return () => {
      this.progressListeners = this.progressListeners.filter(
        (c) => c !== callback
      );
    };
  }

  onError(callback: (e: SyncErrorInfo) => void): () => void {
    this.errorListeners.push(callback);
    return () => {
      this.errorListeners = this.errorListeners.filter((c) => c !== callback);
    };
  }

  onSyncComplete(
    callback: (
      result: SyncResult,
      context: SyncContext
    ) => void | Promise<void>,
    options: CallbackOptions = {}
  ): () => void {
    const entry: RegisteredCallback = { callback, options };
    this.completionCallbacks.push(entry);
    return () => {
      this.completionCallbacks = this.completionCallbacks.filter(
        (e) => e !== entry
      );
    };
  }

  private notifyCompletion(result: SyncResult, context: SyncContext): void {
    for (const entry of this.completionCallbacks) {
      const f = entry.options.filter;
      if (f) {
        if (
          f.syncTypes &&
          !f.syncTypes.includes(
            result.syncType as unknown as import('./sync-types').SyncType
          )
        )
          continue;
        if (f.onSuccess === true && !result.success) continue;
        if (f.onFailure === true && result.success) continue;
      }
      try {
        entry.callback(result, context);
      } catch {
        /* swallow */
      }
      if (entry.options.once) {
        this.completionCallbacks = this.completionCallbacks.filter(
          (e) => e !== entry
        );
      }
    }
  }

  // ---- Helpers ----

  private categorizeHttpError(status: number): ErrorCategory {
    if (status === 401 || status === 403) return ErrorCategory.AUTH_ERROR;
    if (status === 422 || status === 400) return ErrorCategory.VALIDATION_ERROR;
    if (status >= 500) return ErrorCategory.SERVER_ERROR;
    return ErrorCategory.UNKNOWN_ERROR;
  }

  private buildEmptyResult(
    type: SyncType,
    startTime: string,
    success: boolean,
    errors: SyncErrorInfo[] = []
  ): SyncResult {
    const endTime = new Date().toISOString();
    return {
      success,
      syncType: type,
      duration: new Date(endTime).getTime() - new Date(startTime).getTime(),
      startTime,
      endTime,
      stats: {
        transactionsPushed: 0,
        transactionsFailed: 0,
        entitiesPulled: 0,
        conflictsDetected: 0,
        conflictsResolved: 0,
        conflictsManual: 0,
      },
      errors,
      warnings: [],
    };
  }

  getAnalytics(): SyncAnalytics {
    return this.analytics;
  }

  getConflictResolver(): ConflictResolver {
    return this.conflictResolver;
  }

  getConnectionMonitor(): ConnectionMonitor {
    return this.connectionMonitor;
  }
}

export const syncEngine = SyncEngine.getInstance();
