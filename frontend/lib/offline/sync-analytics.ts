// ================================================================
// Sync Analytics — Tasks 69-72
// ================================================================
// Tracks sync performance, success rates, error patterns, and
// generates reports with insights and benchmarks.
// ================================================================

import {
  AVERAGE_SYNC_DURATION_BASELINE,
  AVERAGE_SYNC_DURATION_THRESHOLD,
  SUCCESS_RATE_BASELINE,
  SUCCESS_RATE_THRESHOLD,
  NETWORK_ERROR_RATE_BASELINE,
  NETWORK_ERROR_RATE_THRESHOLD,
  HIGH_CONFLICT_RATE,
  ANALYTICS_RETENTION_DAYS,
  type SyncMetrics,
  type SyncEvent,
  type SyncResult,
  type SyncContext,
  type SyncErrorInfo,
  type ErrorContext,
  type PerformanceBenchmark,
  type SyncReport,
  type Insight,
  type Conflict,
  type ResolutionResult,
} from './sync-types';

function defaultMetrics(): SyncMetrics {
  return {
    totalSyncs: 0,
    syncsToday: 0,
    syncsThisWeek: 0,
    averageSyncsPerDay: 0,
    successfulSyncs: 0,
    failedSyncs: 0,
    successRate: 100,
    averageDuration: 0,
    minDuration: Infinity,
    maxDuration: 0,
    totalDuration: 0,
    totalBytesPushed: 0,
    totalBytesPulled: 0,
    averageBytesPerSync: 0,
    totalTransactionsPushed: 0,
    averageTransactionsPerSync: 0,
    totalConflicts: 0,
    conflictsAutoResolved: 0,
    conflictsManualResolved: 0,
    conflictRate: 0,
    totalErrors: 0,
    errorsByType: {},
    mostCommonError: '',
    lastSyncTime: '',
    averageTimeBetweenSyncs: 0,
    averageNetworkLatency: 0,
    networkErrors: 0,
  };
}

export class SyncAnalytics {
  private metrics: SyncMetrics = defaultMetrics();
  private events: SyncEvent[] = [];
  private activeSyncs = new Map<string, number>(); // syncId → startTimestamp

  // ----------------------------------------------------------------
  // Tracking
  // ----------------------------------------------------------------

  async trackSyncStart(syncId: string): Promise<void> {
    this.activeSyncs.set(syncId, Date.now());
    this.events.push({
      id: `${syncId}-start`,
      syncId,
      event: 'START',
      timestamp: new Date().toISOString(),
    });
  }

  async trackSyncComplete(
    syncId: string,
    result: SyncResult,
    context?: SyncContext
  ): Promise<void> {
    this.activeSyncs.delete(syncId);
    this.events.push({
      id: `${syncId}-complete`,
      syncId,
      event: 'COMPLETE',
      timestamp: new Date().toISOString(),
      result,
      context,
    });
    this.updateMetrics(result);
    await this.saveMetrics();
  }

  async trackError(
    syncId: string,
    error: SyncErrorInfo,
    _context: ErrorContext
  ): Promise<void> {
    this.events.push({
      id: `${syncId}-error-${Date.now()}`,
      syncId,
      event: 'ERROR',
      timestamp: new Date().toISOString(),
    });
    this.metrics.totalErrors++;
    const key = error.category;
    this.metrics.errorsByType[key] = (this.metrics.errorsByType[key] ?? 0) + 1;
    if (error.category === 'NETWORK_ERROR') this.metrics.networkErrors++;
    this.updateMostCommonError();
    await this.saveMetrics();
  }

  async trackConflictResolution(
    _syncId: string,
    _conflict: Conflict,
    resolution: ResolutionResult
  ): Promise<void> {
    this.metrics.totalConflicts++;
    if (resolution.requiresReview) {
      this.metrics.conflictsManualResolved++;
    } else {
      this.metrics.conflictsAutoResolved++;
    }
    this.metrics.conflictRate =
      this.metrics.totalSyncs > 0
        ? this.metrics.totalConflicts / this.metrics.totalSyncs
        : 0;
  }

  // ----------------------------------------------------------------
  // Metrics computation
  // ----------------------------------------------------------------

  private updateMetrics(result: SyncResult): void {
    this.metrics.totalSyncs++;
    if (result.success) {
      this.metrics.successfulSyncs++;
    } else {
      this.metrics.failedSyncs++;
    }
    this.metrics.successRate =
      this.metrics.totalSyncs > 0
        ? (this.metrics.successfulSyncs / this.metrics.totalSyncs) * 100
        : 100;

    this.updateDurationMetrics(result.duration);
    this.updateConflictMetrics(result.stats);
    this.updateErrorMetrics(result.errors);
    this.metrics.totalTransactionsPushed += result.stats.transactionsPushed;
    this.metrics.averageTransactionsPerSync =
      this.metrics.totalSyncs > 0
        ? this.metrics.totalTransactionsPushed / this.metrics.totalSyncs
        : 0;
    this.metrics.lastSyncTime = result.endTime;
  }

  private updateDurationMetrics(duration: number): void {
    this.metrics.totalDuration += duration;
    this.metrics.averageDuration =
      this.metrics.totalDuration / this.metrics.totalSyncs;
    if (duration < this.metrics.minDuration)
      this.metrics.minDuration = duration;
    if (duration > this.metrics.maxDuration)
      this.metrics.maxDuration = duration;
  }

  private updateConflictMetrics(stats: SyncResult['stats']): void {
    this.metrics.totalConflicts += stats.conflictsDetected;
    this.metrics.conflictsAutoResolved += stats.conflictsResolved;
    this.metrics.conflictsManualResolved += stats.conflictsManual;
    this.metrics.conflictRate =
      this.metrics.totalSyncs > 0
        ? this.metrics.totalConflicts / this.metrics.totalSyncs
        : 0;
  }

  private updateErrorMetrics(errors: SyncErrorInfo[]): void {
    for (const e of errors) {
      this.metrics.totalErrors++;
      const key = e.category;
      this.metrics.errorsByType[key] =
        (this.metrics.errorsByType[key] ?? 0) + 1;
      if (e.category === 'NETWORK_ERROR') this.metrics.networkErrors++;
    }
    this.updateMostCommonError();
  }

  private updateMostCommonError(): void {
    let max = 0;
    let maxKey = '';
    for (const [key, count] of Object.entries(this.metrics.errorsByType)) {
      if (count > max) {
        max = count;
        maxKey = key;
      }
    }
    this.metrics.mostCommonError = maxKey;
  }

  // ----------------------------------------------------------------
  // Reporting
  // ----------------------------------------------------------------

  async generateReport(period: 'day' | 'week' | 'month'): Promise<SyncReport> {
    const now = new Date();
    const msMap = { day: 86_400_000, week: 604_800_000, month: 2_592_000_000 };
    const startDate = new Date(now.getTime() - msMap[period]);

    const filtered = this.events.filter(
      (e) => new Date(e.timestamp) >= startDate
    );
    const completions = filtered.filter(
      (e) => e.event === 'COMPLETE' && e.result
    );

    const totalSyncs = completions.length;
    const successful = completions.filter((e) => e.result!.success).length;
    const successRate = totalSyncs > 0 ? (successful / totalSyncs) * 100 : 100;
    const avgDuration =
      totalSyncs > 0
        ? completions.reduce((sum, e) => sum + e.result!.duration, 0) /
          totalSyncs
        : 0;

    const errorCounts: Record<string, number> = {};
    for (const e of filtered) {
      if (e.result) {
        for (const err of e.result.errors) {
          errorCounts[err.category] = (errorCounts[err.category] ?? 0) + 1;
        }
      }
    }
    const totalErrors = Object.values(errorCounts).reduce((a, b) => a + b, 0);
    const topErrors = Object.entries(errorCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([type, count]) => ({
        type,
        count,
        percentage: totalErrors > 0 ? (count / totalErrors) * 100 : 0,
      }));

    return {
      period,
      startDate: startDate.toISOString(),
      endDate: now.toISOString(),
      summary: {
        totalSyncs,
        successRate,
        averageDuration: avgDuration,
        totalDataTransferred: 0,
        topErrors,
      },
      charts: {
        syncsOverTime: { labels: [], successful: [], failed: [] },
        durationTrend: { labels: [], average: [], min: [], max: [] },
        errorDistribution: {
          labels: Object.keys(errorCounts),
          values: Object.values(errorCounts),
        },
      },
      insights: this.generateInsights(this.metrics),
    };
  }

  // ----------------------------------------------------------------
  // Insights
  // ----------------------------------------------------------------

  private generateInsights(m: SyncMetrics): Insight[] {
    const insights: Insight[] = [];

    if (m.successRate < SUCCESS_RATE_THRESHOLD * 100) {
      insights.push({
        type: 'WARNING',
        message: `Sync success rate is ${m.successRate.toFixed(1)}%, below the ${(SUCCESS_RATE_THRESHOLD * 100).toFixed(0)}% threshold.`,
        recommendation: 'Check network stability and server health.',
      });
    } else if (m.successRate >= SUCCESS_RATE_BASELINE * 100) {
      insights.push({
        type: 'SUCCESS',
        message: `Sync success rate is excellent at ${m.successRate.toFixed(1)}%.`,
      });
    }

    if (m.averageDuration > AVERAGE_SYNC_DURATION_THRESHOLD) {
      insights.push({
        type: 'WARNING',
        message: `Average sync duration (${(m.averageDuration / 1000).toFixed(1)}s) exceeds threshold.`,
        recommendation:
          'Consider reducing batch sizes or optimizing server endpoints.',
      });
    }

    if (m.conflictRate > HIGH_CONFLICT_RATE) {
      insights.push({
        type: 'WARNING',
        message: `Conflict rate (${m.conflictRate.toFixed(2)} per sync) is high.`,
        recommendation: 'Increase sync frequency to reduce data staleness.',
      });
    }

    if (m.totalSyncs > 0 && insights.length === 0) {
      insights.push({
        type: 'INFO',
        message: 'All sync metrics are within normal ranges.',
      });
    }

    return insights;
  }

  // ----------------------------------------------------------------
  // Benchmarks
  // ----------------------------------------------------------------

  getPerformanceBenchmarks(): PerformanceBenchmark[] {
    const m = this.metrics;
    return [
      {
        metric: 'Sync Duration (ms)',
        baseline: AVERAGE_SYNC_DURATION_BASELINE,
        current: m.averageDuration,
        threshold: AVERAGE_SYNC_DURATION_THRESHOLD,
        status:
          m.averageDuration <= AVERAGE_SYNC_DURATION_BASELINE
            ? 'GOOD'
            : m.averageDuration <= AVERAGE_SYNC_DURATION_THRESHOLD
              ? 'WARNING'
              : 'CRITICAL',
      },
      {
        metric: 'Success Rate (%)',
        baseline: SUCCESS_RATE_BASELINE * 100,
        current: m.successRate,
        threshold: SUCCESS_RATE_THRESHOLD * 100,
        status:
          m.successRate >= SUCCESS_RATE_BASELINE * 100
            ? 'GOOD'
            : m.successRate >= SUCCESS_RATE_THRESHOLD * 100
              ? 'WARNING'
              : 'CRITICAL',
      },
      {
        metric: 'Network Error Rate',
        baseline: NETWORK_ERROR_RATE_BASELINE,
        current: m.totalSyncs > 0 ? m.networkErrors / m.totalSyncs : 0,
        threshold: NETWORK_ERROR_RATE_THRESHOLD,
        status:
          (m.totalSyncs > 0 ? m.networkErrors / m.totalSyncs : 0) <=
          NETWORK_ERROR_RATE_BASELINE
            ? 'GOOD'
            : m.networkErrors / m.totalSyncs <= NETWORK_ERROR_RATE_THRESHOLD
              ? 'WARNING'
              : 'CRITICAL',
      },
    ];
  }

  // ----------------------------------------------------------------
  // Data export & cleanup
  // ----------------------------------------------------------------

  async exportAnalytics(format: 'json' | 'csv'): Promise<string> {
    if (format === 'json') {
      return JSON.stringify(
        { metrics: this.metrics, events: this.events },
        null,
        2
      );
    }
    const header = 'id,syncId,event,timestamp\n';
    const rows = this.events
      .map((e) => `${e.id},${e.syncId},${e.event},${e.timestamp}`)
      .join('\n');
    return header + rows;
  }

  async purgeOldData(
    daysToKeep: number = ANALYTICS_RETENTION_DAYS
  ): Promise<void> {
    const cutoff = Date.now() - daysToKeep * 86_400_000;
    this.events = this.events.filter(
      (e) => new Date(e.timestamp).getTime() >= cutoff
    );
  }

  getMetrics(): SyncMetrics {
    return { ...this.metrics };
  }

  // ----------------------------------------------------------------
  // Persistence (IndexedDB delegation)
  // ----------------------------------------------------------------

  private async saveMetrics(): Promise<void> {
    // In production, persist to IndexedDB via idbService
    // For now, metrics are held in memory
  }
}

export const syncAnalytics = new SyncAnalytics();
