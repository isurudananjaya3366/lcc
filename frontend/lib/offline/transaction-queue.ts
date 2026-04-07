// ================================================================
// Transaction Queue — Tasks 35-52
// ================================================================
// Offline transaction queue with ordering, dependency tracking,
// retry, validation, export/import, cleanup, and notifications.
// ================================================================

import { idbService } from './indexeddb';
import { ObjectStoreNames } from './schema';
import { generateOfflineTransactionId } from './id-generator';
import { getCurrentTimestamp } from './utils';
import {
  TransactionStatus,
  OrderingStrategy,
  TransactionPriority,
  CleanupStrategy,
  NotificationType,
  NotificationSeverity,
  DEFAULT_QUEUE_CONFIG,
  VALIDATION_RULES,
  QUEUE_SIZE_THRESHOLDS,
  type QueueConfig,
  type QueueMetadata,
  type QueuedTransaction,
  type TransactionPayload,
  type QueueStatusSummary,
  type ValidationResult,
  type ValidationError,
  type ValidationWarning,
  type ErrorDetails,
  type PendingTransactionWithDeps,
  type ExportOptions,
  type QueueExportFile,
  type DependencyGraph,
  type CircularDependency,
  type CleanupResult,
  type IntegrityReport,
  type QueueNotification,
} from './queue-types';

const STORE = ObjectStoreNames.TRANSACTIONS;
const META_STORE = ObjectStoreNames.SETTINGS; // reuse settings store for queue metadata
const META_KEY = '__queue_metadata__';

// ── Event emitter helpers ──────────────────────────────────────

type Listener = (notification: QueueNotification) => void;

// ── Class ──────────────────────────────────────────────────────

export class TransactionQueue {
  private config: QueueConfig;
  private listeners: Listener[] = [];
  private cleanupTimer: ReturnType<typeof setInterval> | null = null;
  private initialised = false;

  constructor(config?: Partial<QueueConfig>) {
    this.config = { ...DEFAULT_QUEUE_CONFIG, ...config };
  }

  // ── Initialisation (Task 45) ─────────────────────────────────

  async initialize(): Promise<void> {
    if (this.initialised) return;
    await idbService.openDatabase();

    // Recover from unclean shutdown
    const meta = await this.loadMetadata();
    if (meta && !meta.clean_shutdown) {
      await this.recoverQueue();
    }

    // Save clean init metadata
    await this.saveMetadata({
      clean_shutdown: false,
      updated_at: getCurrentTimestamp(),
    });

    // Register shutdown handler
    if (typeof globalThis.addEventListener === 'function') {
      globalThis.addEventListener('beforeunload', () => {
        void this.handleShutdown();
      });
    }

    // Schedule automatic cleanup
    if (this.config.cleanupInterval > 0) {
      this.cleanupTimer = setInterval(
        () => void this.cleanupQueue(),
        this.config.cleanupInterval
      );
    }

    this.initialised = true;
  }

  // ── Queue Transaction (Task 36) ─────────────────────────────

  async queueTransaction(
    payload: TransactionPayload,
    dependsOn?: string
  ): Promise<string> {
    await this.initialize();

    // Validate (Task 46)
    const validation = this.validateTransaction(payload);
    if (!validation.isValid) {
      throw new Error(
        `Invalid transaction: ${validation.errors.map((e) => e.message).join('; ')}`
      );
    }

    // Validate dependency (Task 50)
    if (dependsOn) {
      const dep = await idbService.get<QueuedTransaction>(STORE, dependsOn);
      if (!dep) throw new Error(`Dependency ${dependsOn} not found`);
    }

    const offlineId = generateOfflineTransactionId(payload.terminal_id);

    const tx: QueuedTransaction = {
      offline_id: offlineId,
      terminal_id: payload.terminal_id,
      session_id: payload.session_id,
      created_at: getCurrentTimestamp(),
      synced_at: null,
      status: TransactionStatus.PENDING,
      retry_count: 0,
      error_message: null,
      depends_on: dependsOn ?? null,
      payload,
      priority: TransactionPriority.NORMAL,
    };

    await idbService.put(STORE, tx);

    const pending = await this.getQueueLength();
    this.notify(
      NotificationType.TRANSACTION_QUEUED,
      'Transaction Queued',
      `Queued ${offlineId} (position ${pending})`,
      NotificationSeverity.INFO,
      { offline_id: offlineId, position: pending }
    );

    this.checkQueueSizeWarnings(pending);

    return offlineId;
  }

  // ── Position Tracking (Task 38) ─────────────────────────────

  async getTransactionPosition(offlineId: string): Promise<number | null> {
    const pending = await this.getPendingTransactions();
    const idx = pending.findIndex((t) => t.offline_id === offlineId);
    return idx === -1 ? null : idx + 1;
  }

  async getAllPositions(): Promise<Map<string, number>> {
    const pending = await this.getPendingTransactions();
    const map = new Map<string, number>();
    pending.forEach((t, i) => map.set(t.offline_id, i + 1));
    return map;
  }

  async getQueueLength(): Promise<number> {
    const pending = await idbService.getAllByIndex<QueuedTransaction>(
      STORE,
      'sync_status',
      'pending'
    );
    return pending.length;
  }

  // ── Get Pending (Task 39) ───────────────────────────────────

  async getPendingTransactions(options?: {
    limit?: number;
    offset?: number;
    terminal_id?: string;
  }): Promise<QueuedTransaction[]> {
    await this.initialize();
    let all = await idbService.getAll<QueuedTransaction>(STORE);
    all = all.filter((t) => t.status === TransactionStatus.PENDING);

    if (options?.terminal_id) {
      all = all.filter((t) => t.terminal_id === options.terminal_id);
    }

    // Sort per current ordering strategy
    all = this.sortByStrategy(all);

    const offset = options?.offset ?? 0;
    const limit = options?.limit ?? all.length;
    return all.slice(offset, offset + limit);
  }

  async getPendingWithDependencies(): Promise<PendingTransactionWithDeps[]> {
    const pending = await this.getPendingTransactions();
    const allTx = await idbService.getAll<QueuedTransaction>(STORE);
    const txMap = new Map(allTx.map((t) => [t.offline_id, t]));

    return pending.map((t, i) => ({
      ...t,
      position: i + 1,
      dependency_status: t.depends_on
        ? txMap.get(t.depends_on)?.status
        : undefined,
    }));
  }

  // ── Mark as Synced (Task 40) ─────────────────────────────────

  async markAsSynced(
    offlineId: string,
    serverTransactionId: string
  ): Promise<boolean> {
    const tx = await idbService.get<QueuedTransaction>(STORE, offlineId);
    if (!tx) return false;

    tx.status = TransactionStatus.SYNCED;
    tx.synced_at = getCurrentTimestamp();
    tx.server_transaction_id = serverTransactionId;
    await idbService.put(STORE, tx);

    await this.saveMetadata({ last_successful_sync: getCurrentTimestamp() });

    // Notify dependents (Task 50)
    await this.notifyDependents(offlineId);

    this.notify(
      NotificationType.TRANSACTION_SYNCED,
      'Transaction Synced',
      `${offlineId} synced to server`,
      NotificationSeverity.SUCCESS,
      { offline_id: offlineId, server_transaction_id: serverTransactionId }
    );

    return true;
  }

  // ── Mark as Failed (Task 41) ─────────────────────────────────

  async markAsFailed(
    offlineId: string,
    errorMessage: string,
    errorDetails?: ErrorDetails
  ): Promise<boolean> {
    const tx = await idbService.get<QueuedTransaction>(STORE, offlineId);
    if (!tx) return false;

    tx.retry_count += 1;
    tx.error_message = errorMessage;
    tx.last_error_at = getCurrentTimestamp();
    if (errorDetails) tx.error_details = errorDetails;

    if (tx.retry_count >= this.config.maxRetries) {
      tx.status = TransactionStatus.FAILED;
      this.notify(
        NotificationType.TRANSACTION_FAILED,
        'Transaction Failed',
        `${offlineId} permanently failed after ${tx.retry_count} retries`,
        NotificationSeverity.ERROR,
        {
          offline_id: offlineId,
          retry_count: tx.retry_count,
          error_message: errorMessage,
        }
      );
    } else {
      tx.status = TransactionStatus.PENDING;
      const delay =
        this.config.retryDelays[
          Math.min(tx.retry_count - 1, this.config.retryDelays.length - 1)
        ] ?? 30000;
      tx.next_retry_at = new Date(Date.now() + delay).toISOString();
    }

    await idbService.put(STORE, tx);
    await this.saveMetadata({ last_sync_attempt: getCurrentTimestamp() });
    return true;
  }

  // ── Config (Task 43) ────────────────────────────────────────

  getMaxRetries(): number {
    return this.config.maxRetries;
  }

  setMaxRetries(limit: number): void {
    if (limit < 1 || limit > 10)
      throw new RangeError('maxRetries must be 1-10');
    this.config.maxRetries = limit;
  }

  // ── Queue Status (Task 44) ──────────────────────────────────

  async getQueueStatus(): Promise<QueueStatusSummary> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    const counts = { pending: 0, syncing: 0, synced: 0, failed: 0 };
    let totalRetries = 0;
    let maxRetries = 0;
    let atMax = 0;
    let oldestPending: string | null = null;
    const errorCounts = new Map<string, number>();

    for (const tx of all) {
      counts[tx.status.toLowerCase() as keyof typeof counts] += 1;
      totalRetries += tx.retry_count;
      if (tx.retry_count > maxRetries) maxRetries = tx.retry_count;
      if (tx.retry_count >= this.config.maxRetries) atMax++;

      if (tx.status === TransactionStatus.PENDING) {
        if (!oldestPending || tx.created_at < oldestPending)
          oldestPending = tx.created_at;
      }
      if (tx.error_message) {
        errorCounts.set(
          tx.error_message,
          (errorCounts.get(tx.error_message) ?? 0) + 1
        );
      }
    }

    const total = all.length;
    const avgRetry = total > 0 ? totalRetries / total : 0;

    // Error distribution
    const errorDist = Array.from(errorCounts.entries())
      .map(([error, count]) => ({ error, count }))
      .sort((a, b) => b.count - a.count);

    const meta = await this.loadMetadata();

    const summary: QueueStatusSummary = {
      ...counts,
      total,
      oldest_pending: oldestPending,
      last_sync_attempt: meta?.last_sync_attempt ?? null,
      last_successful_sync: meta?.last_successful_sync ?? null,
      average_retry_count: Math.round(avgRetry * 100) / 100,
      max_retry_count: maxRetries,
      at_max_retries: atMax,
      health_score: 0,
      estimated_clear_time: counts.pending > 0 ? counts.pending * 2 : null,
      oldest_pending_age: oldestPending
        ? (Date.now() - new Date(oldestPending).getTime()) / 1000
        : null,
      error_summary: {
        most_common_error: errorDist[0]?.error ?? null,
        error_count: errorDist.reduce((s, e) => s + e.count, 0),
        error_distribution: errorDist,
      },
    };

    summary.health_score = this.calculateHealthScore(summary);
    return summary;
  }

  private calculateHealthScore(s: QueueStatusSummary): number {
    let score = 100;
    if (s.total === 0) return 100;

    // Failed percentage penalty (max 30)
    score -= Math.round((s.failed / s.total) * 30);
    // Retry penalty (max 30)
    score -= Math.round((s.average_retry_count / this.config.maxRetries) * 30);
    // Age penalty (max 20) — 1 hour = max
    const ageSeconds = s.oldest_pending_age ?? 0;
    score -= Math.round(Math.min(ageSeconds / 3600, 1) * 20);
    // Backlog penalty (max 20) — 100+ = max
    score -= Math.round(Math.min(s.pending / 100, 1) * 20);

    return Math.max(0, Math.min(100, score));
  }

  // ── Validation (Task 46) ────────────────────────────────────

  validateTransaction(payload: TransactionPayload): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Required fields
    if (!payload.terminal_id)
      errors.push({
        field: 'terminal_id',
        code: 'REQUIRED',
        message: 'terminal_id is required',
      });
    else if (
      payload.terminal_id.length < VALIDATION_RULES.MIN_TERMINAL_ID_LEN ||
      payload.terminal_id.length > VALIDATION_RULES.MAX_TERMINAL_ID_LEN
    )
      errors.push({
        field: 'terminal_id',
        code: 'LENGTH',
        message: `terminal_id must be ${VALIDATION_RULES.MIN_TERMINAL_ID_LEN}-${VALIDATION_RULES.MAX_TERMINAL_ID_LEN} chars`,
        value: payload.terminal_id,
      });

    if (!payload.session_id)
      errors.push({
        field: 'session_id',
        code: 'REQUIRED',
        message: 'session_id is required',
      });
    if (!payload.payment_method)
      errors.push({
        field: 'payment_method',
        code: 'REQUIRED',
        message: 'payment_method is required',
      });
    if (!payload.timestamp)
      errors.push({
        field: 'timestamp',
        code: 'REQUIRED',
        message: 'timestamp is required',
      });

    // Items
    if (!Array.isArray(payload.items) || payload.items.length === 0)
      errors.push({
        field: 'items',
        code: 'REQUIRED',
        message: 'items must be a non-empty array',
      });
    else if (payload.items.length > VALIDATION_RULES.MAX_ITEMS)
      errors.push({
        field: 'items',
        code: 'MAX_EXCEEDED',
        message: `items must not exceed ${VALIDATION_RULES.MAX_ITEMS}`,
        value: payload.items.length,
      });
    else {
      for (let i = 0; i < payload.items.length; i++) {
        const item = payload.items[i]!;
        if (!item.product_id)
          errors.push({
            field: `items[${i}].product_id`,
            code: 'REQUIRED',
            message: 'product_id is required',
          });
        if (item.quantity <= 0)
          errors.push({
            field: `items[${i}].quantity`,
            code: 'RANGE',
            message: 'quantity must be > 0',
            value: item.quantity,
          });
        if (item.quantity > VALIDATION_RULES.MAX_ITEM_QUANTITY)
          errors.push({
            field: `items[${i}].quantity`,
            code: 'MAX_EXCEEDED',
            message: `quantity must not exceed ${VALIDATION_RULES.MAX_ITEM_QUANTITY}`,
            value: item.quantity,
          });
        if (item.price < 0)
          errors.push({
            field: `items[${i}].price`,
            code: 'RANGE',
            message: 'price must be >= 0',
            value: item.price,
          });
      }
    }

    // Grand total
    if (payload.grand_total < VALIDATION_RULES.MIN_GRAND_TOTAL)
      errors.push({
        field: 'grand_total',
        code: 'RANGE',
        message: `grand_total must be >= ${VALIDATION_RULES.MIN_GRAND_TOTAL}`,
        value: payload.grand_total,
      });
    if (payload.grand_total > VALIDATION_RULES.MAX_GRAND_TOTAL)
      errors.push({
        field: 'grand_total',
        code: 'MAX_EXCEEDED',
        message: `grand_total must be <= ${VALIDATION_RULES.MAX_GRAND_TOTAL}`,
        value: payload.grand_total,
      });

    // Calculation check
    if (payload.items?.length > 0) {
      const computedSubtotal = payload.items.reduce(
        (s, item) => s + item.subtotal,
        0
      );
      if (
        Math.abs(computedSubtotal - payload.subtotal) >
        VALIDATION_RULES.ROUNDING_TOLERANCE
      ) {
        warnings.push({
          field: 'subtotal',
          code: 'CALC_MISMATCH',
          message: `subtotal ${payload.subtotal} does not match items sum ${computedSubtotal}`,
        });
      }
    }

    // Timestamp sanity
    if (payload.timestamp) {
      const ts = new Date(payload.timestamp).getTime();
      const now = Date.now();
      if (ts > now + VALIDATION_RULES.TIMESTAMP_FUTURE_TOLERANCE_S * 1000)
        warnings.push({
          field: 'timestamp',
          code: 'FUTURE',
          message: 'timestamp is in the future',
        });
      if (ts < now - VALIDATION_RULES.TIMESTAMP_AGE_WARNING_S * 1000)
        warnings.push({
          field: 'timestamp',
          code: 'OLD',
          message: 'timestamp is older than 30 days',
        });
    }

    return { isValid: errors.length === 0, errors, warnings };
  }

  async checkQueueIntegrity(): Promise<IntegrityReport> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    const report: IntegrityReport = {
      total_checked: all.length,
      valid: 0,
      invalid: 0,
      warnings: 0,
      invalid_transactions: [],
    };

    for (const tx of all) {
      const result = this.validateTransaction(tx.payload);
      if (result.isValid) {
        report.valid++;
      } else {
        report.invalid++;
        report.invalid_transactions.push({
          offline_id: tx.offline_id,
          errors: result.errors,
        });
      }
      if (result.warnings.length > 0) report.warnings += result.warnings.length;
    }

    return report;
  }

  // ── Ordering (Task 49) ──────────────────────────────────────

  async getNextTransaction(): Promise<QueuedTransaction | null> {
    const batch = await this.getNextBatch(1);
    return batch[0] ?? null;
  }

  async getNextBatch(batchSize: number): Promise<QueuedTransaction[]> {
    const pending = await this.getPendingTransactions();

    // Exclude transactions whose dependency is not yet synced
    const eligible = [];
    for (const tx of pending) {
      if (await this.canProcess(tx.offline_id)) eligible.push(tx);
      if (eligible.length >= batchSize) break;
    }
    return eligible;
  }

  async reorderQueue(strategy: OrderingStrategy): Promise<void> {
    this.config.orderingStrategy = strategy;
  }

  private sortByStrategy(txs: QueuedTransaction[]): QueuedTransaction[] {
    switch (this.config.orderingStrategy) {
      case OrderingStrategy.LIFO:
        return txs.sort((a, b) => b.created_at.localeCompare(a.created_at));
      case OrderingStrategy.PRIORITY:
        return txs.sort(
          (a, b) =>
            (b.priority ?? TransactionPriority.NORMAL) -
            (a.priority ?? TransactionPriority.NORMAL)
        );
      case OrderingStrategy.DEPENDENCY_AWARE:
        return this.sortDependencyAware(txs);
      case OrderingStrategy.FIFO:
      default:
        return txs.sort((a, b) => a.created_at.localeCompare(b.created_at));
    }
  }

  private sortDependencyAware(txs: QueuedTransaction[]): QueuedTransaction[] {
    // Topological sort: dependencies first
    const idSet = new Set(txs.map((t) => t.offline_id));
    const visited = new Set<string>();
    const ordered: QueuedTransaction[] = [];
    const txMap = new Map(txs.map((t) => [t.offline_id, t]));

    const visit = (id: string) => {
      if (visited.has(id)) return;
      visited.add(id);
      const tx = txMap.get(id);
      if (!tx) return;
      if (tx.depends_on && idSet.has(tx.depends_on)) {
        visit(tx.depends_on);
      }
      ordered.push(tx);
    };

    for (const tx of txs) visit(tx.offline_id);
    return ordered;
  }

  // ── Dependency Tracking (Task 50) ───────────────────────────

  async canProcess(offlineId: string): Promise<boolean> {
    const tx = await idbService.get<QueuedTransaction>(STORE, offlineId);
    if (!tx) return false;
    if (!tx.depends_on) return true;
    const dep = await idbService.get<QueuedTransaction>(STORE, tx.depends_on);
    return dep?.status === TransactionStatus.SYNCED;
  }

  async getDependency(offlineId: string): Promise<QueuedTransaction | null> {
    const tx = await idbService.get<QueuedTransaction>(STORE, offlineId);
    if (!tx?.depends_on) return null;
    return (
      (await idbService.get<QueuedTransaction>(STORE, tx.depends_on)) ?? null
    );
  }

  async getDependents(offlineId: string): Promise<QueuedTransaction[]> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    return all.filter((t) => t.depends_on === offlineId);
  }

  async getDependencyChain(offlineId: string): Promise<QueuedTransaction[]> {
    const chain: QueuedTransaction[] = [];
    let current = await idbService.get<QueuedTransaction>(STORE, offlineId);
    const visited = new Set<string>();

    while (current?.depends_on && !visited.has(current.depends_on)) {
      visited.add(current.depends_on);
      const dep = await idbService.get<QueuedTransaction>(
        STORE,
        current.depends_on
      );
      if (!dep) break;
      chain.unshift(dep);
      current = dep;
    }

    return chain;
  }

  async buildDependencyGraph(): Promise<DependencyGraph> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    const graph: DependencyGraph = {
      nodes: new Map(all.map((t) => [t.offline_id, t])),
      edges: new Map(),
      roots: [],
      leaves: [],
    };

    const hasDependent = new Set<string>();
    for (const tx of all) {
      if (tx.depends_on) {
        hasDependent.add(tx.depends_on);
        const existing = graph.edges.get(tx.depends_on) ?? [];
        existing.push(tx.offline_id);
        graph.edges.set(tx.depends_on, existing);
      }
    }

    for (const tx of all) {
      if (!tx.depends_on) graph.roots.push(tx.offline_id);
      if (!hasDependent.has(tx.offline_id)) graph.leaves.push(tx.offline_id);
    }

    return graph;
  }

  async detectCircularDependencies(): Promise<CircularDependency[]> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    const depsMap = new Map<string, string>();
    for (const tx of all) {
      if (tx.depends_on) depsMap.set(tx.offline_id, tx.depends_on);
    }

    const circles: CircularDependency[] = [];
    const checked = new Set<string>();

    for (const [id] of depsMap) {
      if (checked.has(id)) continue;
      const path: string[] = [];
      let current: string | undefined = id;

      while (current && !checked.has(current)) {
        if (path.includes(current)) {
          const cycleStart = path.indexOf(current);
          circles.push({
            transactions: path.slice(cycleStart),
            detected_at: getCurrentTimestamp(),
            resolution: 'MARK_FAILED',
          });
          break;
        }
        path.push(current);
        current = depsMap.get(current);
      }

      for (const p of path) checked.add(p);
    }

    return circles;
  }

  private async notifyDependents(syncedId: string): Promise<void> {
    const dependents = await this.getDependents(syncedId);
    if (dependents.length > 0) {
      this.notify(
        NotificationType.DEPENDENCY_RESOLVED,
        'Dependency Resolved',
        `${syncedId} synced — ${dependents.length} dependent(s) now eligible`,
        NotificationSeverity.INFO,
        {
          offline_id: syncedId,
          dependents: dependents.map((d) => d.offline_id),
        }
      );
    }
  }

  // ── Export (Task 47) ────────────────────────────────────────

  async exportQueue(options?: ExportOptions): Promise<string> {
    let all = await idbService.getAll<QueuedTransaction>(STORE);

    if (options?.include_statuses?.length) {
      all = all.filter((t) => options.include_statuses!.includes(t.status));
    }
    if (!options?.include_synced) {
      all = all.filter((t) => t.status !== TransactionStatus.SYNCED);
    }
    if (options?.date_from)
      all = all.filter((t) => t.created_at >= options.date_from!);
    if (options?.date_to)
      all = all.filter((t) => t.created_at <= options.date_to!);
    if (options?.terminal_id)
      all = all.filter((t) => t.terminal_id === options.terminal_id);

    const meta = await this.loadMetadata();

    const file: QueueExportFile = {
      export_version: '1.0',
      schema_version: '1.0',
      exported_at: getCurrentTimestamp(),
      terminal_id: meta?.session_id ?? '',
      session_id: meta?.session_id ?? '',
      configuration: this.config,
      metadata: {
        transaction_count: all.length,
        included_statuses: [...new Set(all.map((t) => t.status))],
        date_range: {
          from:
            all.length > 0
              ? all.reduce(
                  (m, t) => (t.created_at < m ? t.created_at : m),
                  all[0]!.created_at
                )
              : null,
          to:
            all.length > 0
              ? all.reduce(
                  (m, t) => (t.created_at > m ? t.created_at : m),
                  all[0]!.created_at
                )
              : null,
        },
      },
      transactions: all,
      checksum: '',
    };

    file.checksum = this.generateChecksum(all);

    this.notify(
      NotificationType.EXPORT_COMPLETE,
      'Export Complete',
      `Exported ${all.length} transactions`,
      NotificationSeverity.SUCCESS
    );

    return JSON.stringify(file, null, 2);
  }

  async downloadExportFile(filename?: string): Promise<void> {
    const json = await this.exportQueue({ include_synced: true });
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename ?? `pos-queue-export-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Import (Task 48) ───────────────────────────────────────

  async importQueue(jsonString: string): Promise<{
    imported_count: number;
    skipped_count: number;
    errors: Array<{ offline_id: string; error: string }>;
  }> {
    const file: QueueExportFile = JSON.parse(jsonString);
    if (!this.validateImportFile(file)) throw new Error('Invalid export file');

    const checksum = this.generateChecksum(file.transactions);
    if (file.checksum && file.checksum !== checksum) {
      throw new Error('Checksum mismatch — file may be corrupted');
    }

    let imported = 0;
    let skipped = 0;
    const errors: Array<{ offline_id: string; error: string }> = [];

    for (const tx of file.transactions) {
      try {
        const existing = await idbService.get(STORE, tx.offline_id);
        if (existing) {
          skipped++;
          continue;
        }
        await idbService.put(STORE, tx);
        imported++;
      } catch (err) {
        errors.push({ offline_id: tx.offline_id, error: String(err) });
      }
    }

    return { imported_count: imported, skipped_count: skipped, errors };
  }

  private validateImportFile(file: QueueExportFile): boolean {
    return !!(
      file.export_version &&
      file.schema_version &&
      Array.isArray(file.transactions)
    );
  }

  private generateChecksum(transactions: QueuedTransaction[]): string {
    // Simple hash based on concatenated IDs + count
    const ids = transactions
      .map((t) => t.offline_id)
      .sort()
      .join('|');
    let hash = 0;
    for (let i = 0; i < ids.length; i++) {
      hash = ((hash << 5) - hash + ids.charCodeAt(i)) | 0;
    }
    return `chk_${Math.abs(hash).toString(36)}_${transactions.length}`;
  }

  // ── Cleanup (Task 52) ──────────────────────────────────────

  async cleanupQueue(strategy?: CleanupStrategy): Promise<CleanupResult> {
    const s = strategy ?? this.config.cleanupStrategy;
    const start = Date.now();

    switch (s) {
      case CleanupStrategy.COUNT_BASED:
        return this.cleanupByCount(start);
      case CleanupStrategy.STORAGE_BASED:
        return this.cleanupByStorage(start);
      case CleanupStrategy.MANUAL:
        return {
          total_scanned: 0,
          removed: 0,
          kept: 0,
          duration_ms: 0,
          strategy: s,
          timestamp: getCurrentTimestamp(),
        };
      case CleanupStrategy.AGE_BASED:
      default:
        return this.cleanupByAge(start);
    }
  }

  async cleanupNow(): Promise<CleanupResult> {
    return this.cleanupQueue();
  }

  private async cleanupByAge(start: number): Promise<CleanupResult> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    const cutoff = new Date(
      Date.now() - this.config.cleanupThreshold
    ).toISOString();
    const toRemove = all.filter(
      (t) =>
        t.status === TransactionStatus.SYNCED &&
        t.synced_at &&
        t.synced_at < cutoff
    );

    if (toRemove.length > 0) {
      await idbService.bulkDelete(
        STORE,
        toRemove.map((t) => t.offline_id)
      );
    }

    return {
      total_scanned: all.length,
      removed: toRemove.length,
      kept: all.length - toRemove.length,
      duration_ms: Date.now() - start,
      strategy: CleanupStrategy.AGE_BASED,
      timestamp: getCurrentTimestamp(),
    };
  }

  private async cleanupByCount(start: number): Promise<CleanupResult> {
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    const synced = all
      .filter((t) => t.status === TransactionStatus.SYNCED)
      .sort((a, b) => (a.synced_at ?? '').localeCompare(b.synced_at ?? ''));

    const excess = synced.length - this.config.maxSyncedTransactions;
    const toRemove = excess > 0 ? synced.slice(0, excess) : [];

    if (toRemove.length > 0) {
      await idbService.bulkDelete(
        STORE,
        toRemove.map((t) => t.offline_id)
      );
    }

    return {
      total_scanned: all.length,
      removed: toRemove.length,
      kept: all.length - toRemove.length,
      duration_ms: Date.now() - start,
      strategy: CleanupStrategy.COUNT_BASED,
      timestamp: getCurrentTimestamp(),
    };
  }

  private async cleanupByStorage(start: number): Promise<CleanupResult> {
    // Fall back to age-based if Storage API unavailable
    if (typeof navigator === 'undefined' || !navigator.storage?.estimate) {
      return this.cleanupByAge(start);
    }

    const est = await navigator.storage.estimate();
    const used = est.usage ?? 0;
    const quota = est.quota ?? 0;
    if (quota === 0 || used / quota < 0.8) {
      return {
        total_scanned: 0,
        removed: 0,
        kept: 0,
        duration_ms: Date.now() - start,
        strategy: CleanupStrategy.STORAGE_BASED,
        timestamp: getCurrentTimestamp(),
      };
    }

    return this.cleanupByAge(start);
  }

  // ── Notifications (Task 51) ─────────────────────────────────

  addNotificationListener(callback: Listener): () => void {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== callback);
    };
  }

  private notify(
    type: NotificationType,
    title: string,
    message: string,
    severity: NotificationSeverity,
    metadata?: Record<string, unknown>
  ): void {
    const notification: QueueNotification = {
      id: `notif_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      type,
      title,
      message,
      severity,
      timestamp: getCurrentTimestamp(),
      metadata,
    };

    for (const listener of this.listeners) {
      try {
        listener(notification);
      } catch {
        /* ignore */
      }
    }
  }

  private checkQueueSizeWarnings(size: number): void {
    for (const threshold of QUEUE_SIZE_THRESHOLDS) {
      if (size === threshold) {
        this.notify(
          NotificationType.QUEUE_SIZE_WARNING,
          'Queue Size Warning',
          `Queue has reached ${threshold} pending transactions`,
          NotificationSeverity.WARNING,
          { queue_size: size }
        );
      }
    }
  }

  // ── Persistence helpers (Task 45) ───────────────────────────

  private async loadMetadata(): Promise<QueueMetadata | null> {
    const setting = await idbService.get<{ key: string; value: QueueMetadata }>(
      META_STORE,
      META_KEY
    );
    return setting?.value ?? null;
  }

  private async saveMetadata(updates: Partial<QueueMetadata>): Promise<void> {
    const existing = await this.loadMetadata();
    const meta: QueueMetadata = {
      version: '1.0',
      session_id: '',
      last_sync_attempt: null,
      last_successful_sync: null,
      clean_shutdown: false,
      configuration: this.config,
      created_at: existing?.created_at ?? getCurrentTimestamp(),
      updated_at: getCurrentTimestamp(),
      ...existing,
      ...updates,
    };
    await idbService.put(META_STORE, {
      key: META_KEY,
      value: meta,
      updated_at: getCurrentTimestamp(),
    });
  }

  private async recoverQueue(): Promise<void> {
    // Reset any SYNCING transactions back to PENDING (unclean shutdown)
    const all = await idbService.getAll<QueuedTransaction>(STORE);
    for (const tx of all) {
      if (tx.status === TransactionStatus.SYNCING) {
        tx.status = TransactionStatus.PENDING;
        await idbService.put(STORE, tx);
      }
    }
  }

  private async handleShutdown(): Promise<void> {
    await this.saveMetadata({ clean_shutdown: true });
  }

  // ── Destroy ─────────────────────────────────────────────────

  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
      this.cleanupTimer = null;
    }
    this.listeners = [];
  }
}
