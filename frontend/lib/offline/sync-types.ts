// ================================================================
// Sync Engine Types — Tasks 53-72
// ================================================================
// All enums, interfaces, and constants for the sync engine.
// ================================================================

// ----------------------------------------------------------------
// Enums
// ----------------------------------------------------------------

export enum SyncStatus {
  IDLE = 'IDLE',
  CONNECTING = 'CONNECTING',
  PUSHING = 'PUSHING',
  PULLING = 'PULLING',
  RESOLVING_CONFLICTS = 'RESOLVING_CONFLICTS',
  COMPLETED = 'COMPLETED',
  ERROR = 'ERROR',
}

export enum SyncPhase {
  INITIALIZING = 'INITIALIZING',
  PUSHING = 'PUSHING',
  PULLING = 'PULLING',
  RESOLVING = 'RESOLVING',
  FINALIZING = 'FINALIZING',
  COMPLETED = 'COMPLETED',
}

export enum SyncType {
  PUSH = 'push',
  PULL = 'pull',
  FULL = 'full',
}

export enum ErrorCategory {
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  DATA_ERROR = 'DATA_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

export enum ErrorSeverity {
  FATAL = 'FATAL',
  ERROR = 'ERROR',
  WARNING = 'WARNING',
  INFO = 'INFO',
}

export enum ConnectionQuality {
  OFFLINE = 'offline',
  SLOW = 'slow',
  NORMAL = 'normal',
  FAST = 'fast',
}

export enum ConflictType {
  UPDATE_CONFLICT = 'UPDATE_CONFLICT',
  DELETE_CONFLICT = 'DELETE_CONFLICT',
  STOCK_CONFLICT = 'STOCK_CONFLICT',
  PRICE_CONFLICT = 'PRICE_CONFLICT',
  DATA_INTEGRITY = 'DATA_INTEGRITY',
}

export enum ConflictPriority {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

export enum ConflictResolutionStatus {
  DETECTED = 'DETECTED',
  RESOLVED = 'RESOLVED',
  MANUAL = 'MANUAL',
}

export enum ResolutionStrategy {
  SERVER_WINS = 'SERVER_WINS',
  MERGE = 'MERGE',
  MANUAL = 'MANUAL',
  STOCK_CONFLICT_HANDLER = 'STOCK_CONFLICT_HANDLER',
  PRICE_CONFLICT_HANDLER = 'PRICE_CONFLICT_HANDLER',
}

// ----------------------------------------------------------------
// Sync Engine Interfaces
// ----------------------------------------------------------------

export interface SyncEngineConfig {
  apiEndpoint: string;
  syncInterval: number;
  maxRetryAttempts: number;
  batchSize: number;
  requestTimeout: number;
  pushTimeout: number;
  pullTimeout: number;
  minSyncCooldown: number;
  autoSyncEnabled: boolean;
  backgroundSyncEnabled: boolean;
}

export interface SyncProgress {
  phase: SyncPhase;
  phaseDescription: string;
  percentage: number;
  current: number;
  total: number;
  currentOperation: string;
  startTime: string;
  elapsedTime: number;
  estimatedTimeRemaining?: number;
  itemsPerSecond?: number;
}

export interface SyncResult {
  success: boolean;
  syncType: SyncType;
  duration: number;
  startTime: string;
  endTime: string;
  stats: {
    transactionsPushed: number;
    transactionsFailed: number;
    entitiesPulled: number;
    conflictsDetected: number;
    conflictsResolved: number;
    conflictsManual: number;
  };
  errors: SyncErrorInfo[];
  warnings: string[];
}

export interface SyncErrorInfo {
  code: string;
  message: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  retryable: boolean;
}

export interface SyncContext {
  terminalId: string;
  syncId: string;
  triggeredBy: 'auto' | 'manual' | 'scheduled';
  affectedEntities: {
    type: string;
    ids: string[];
  }[];
  metadata?: Record<string, unknown>;
}

export interface ErrorContext {
  operation: string;
  phase: SyncPhase;
  terminalId: string;
  timestamp: string;
  requestData?: unknown;
  responseData?: unknown;
  retryCount: number;
  maxRetries: number;
  additionalInfo?: Record<string, unknown>;
}

export interface BackoffConfig {
  initialDelay: number;
  maxDelay: number;
  multiplier: number;
  maxAttempts: number;
  jitterFactor: number;
  resetOnSuccess: boolean;
}

export interface ConnectionStatus {
  online: boolean;
  previouslyOnline: boolean;
  timestamp: number;
  quality: ConnectionQuality;
  verified: boolean;
  latency?: number;
}

export interface ConnectionChangeEvent {
  online: boolean;
  previouslyOnline: boolean;
  timestamp: number;
  quality: ConnectionQuality;
  verified: boolean;
  latency?: number;
}

// ----------------------------------------------------------------
// Conflict Resolver Interfaces
// ----------------------------------------------------------------

export interface Conflict {
  id: string;
  type: ConflictType;
  entityType: string;
  entityId: string;
  localData: unknown;
  serverData: unknown;
  localModifiedAt: string;
  serverModifiedAt: string;
  detectedAt: string;
  priority: ConflictPriority;
  status: ConflictResolutionStatus;
  resolutionStrategy?: ResolutionStrategy;
  resolvedAt?: string;
  resolvedBy?: string;
  metadata?: Record<string, unknown>;
}

export interface FieldConflict {
  field: string;
  localValue: unknown;
  serverValue: unknown;
  canAutoMerge: boolean;
  mergeStrategy?: 'local' | 'server' | 'union' | 'calculated' | 'manual';
}

export interface ResolutionResult {
  success: boolean;
  conflictId: string;
  strategy: ResolutionStrategy;
  resolvedAt: string;
  discardedLocalChanges: unknown;
  appliedServerChanges: unknown;
  affectedEntities: string[];
  requiresReview: boolean;
  errors?: string[];
  auditTrail?: AuditTrailEntry;
}

export interface AuditTrailEntry {
  conflictId: string;
  resolvedAt: string;
  strategy: ResolutionStrategy;
  entityType: string;
  entityId: string;
  before: unknown;
  after: unknown;
  discardedFields: string[];
  impact: {
    transactionsAffected: number;
    requiresReview: boolean;
  };
}

export interface ManualResolution {
  id: string;
  conflictId: string;
  priority: ConflictPriority;
  entityType: string;
  entityId: string;
  conflictType: ConflictType;
  localData: unknown;
  serverData: unknown;
  suggestedResolution: string;
  status: 'PENDING' | 'ASSIGNED' | 'IN_REVIEW' | 'RESOLVED' | 'ESCALATED';
  assignedTo?: string;
  createdAt: string;
  dueBy: string;
  resolvedAt?: string;
  resolvedBy?: string;
  resolution?: string;
  notes?: string;
}

export interface StockMovement {
  productId: string;
  type: 'SALE' | 'RETURN' | 'ADJUSTMENT' | 'RECEIVE' | 'TRANSFER';
  quantity: number;
  timestamp: string;
  source: 'local' | 'server';
  terminalId?: string;
}

export interface PriceConflictMetadata {
  conflictId: string;
  productId: string;
  oldPrice: number;
  newPrice: number;
  priceChange: number;
  percentChange: number;
  affectedTransactions: {
    count: number;
    ids: string[];
    totalImpact: number;
  };
  resolutionStrategy: 'AUTO_ACCEPT' | 'FLAGGED' | 'MANUAL';
  managerDecision?: {
    decision: 'ACCEPT_LOSS' | 'ADJUST_INVOICES' | 'SPLIT' | 'OTHER';
    notes: string;
    decidedBy: string;
    decidedAt: string;
  };
}

export interface MergeMetadata {
  strategy: 'MERGE';
  mergedAt: string;
  localChangedFields: string[];
  serverChangedFields: string[];
  conflictingFields: string[];
  resolutions: Record<
    string,
    'local' | 'server' | 'union' | 'calculated' | 'manual'
  >;
  manualReviewRequired: boolean;
  confidenceScore: number;
}

// ----------------------------------------------------------------
// Analytics Interfaces
// ----------------------------------------------------------------

export interface SyncMetrics {
  totalSyncs: number;
  syncsToday: number;
  syncsThisWeek: number;
  averageSyncsPerDay: number;
  successfulSyncs: number;
  failedSyncs: number;
  successRate: number;
  averageDuration: number;
  minDuration: number;
  maxDuration: number;
  totalDuration: number;
  totalBytesPushed: number;
  totalBytesPulled: number;
  averageBytesPerSync: number;
  totalTransactionsPushed: number;
  averageTransactionsPerSync: number;
  totalConflicts: number;
  conflictsAutoResolved: number;
  conflictsManualResolved: number;
  conflictRate: number;
  totalErrors: number;
  errorsByType: Record<string, number>;
  mostCommonError: string;
  lastSyncTime: string;
  averageTimeBetweenSyncs: number;
  averageNetworkLatency: number;
  networkErrors: number;
}

export interface SyncEvent {
  id: string;
  syncId: string;
  event: 'START' | 'COMPLETE' | 'ERROR';
  timestamp: string;
  result?: SyncResult;
  context?: SyncContext;
}

export interface SyncAnalyticsRecord {
  id: string;
  date: string;
  metrics: SyncMetrics;
  hourly: { hour: number; syncs: number; successRate: number }[];
  errors: { type: string; count: number; samples: string[] }[];
}

export interface PerformanceBenchmark {
  metric: string;
  baseline: number;
  current: number;
  threshold: number;
  status: 'GOOD' | 'WARNING' | 'CRITICAL';
}

export interface SyncReport {
  period: 'day' | 'week' | 'month';
  startDate: string;
  endDate: string;
  summary: {
    totalSyncs: number;
    successRate: number;
    averageDuration: number;
    totalDataTransferred: number;
    topErrors: { type: string; count: number; percentage: number }[];
  };
  charts: {
    syncsOverTime: { labels: string[]; successful: number[]; failed: number[] };
    durationTrend: {
      labels: string[];
      average: number[];
      min: number[];
      max: number[];
    };
    errorDistribution: { labels: string[]; values: number[] };
  };
  insights: Insight[];
}

export interface Insight {
  type: 'INFO' | 'WARNING' | 'SUCCESS';
  message: string;
  recommendation?: string;
}

// ----------------------------------------------------------------
// Delta Sync Types (Task 61)
// ----------------------------------------------------------------

export interface DeltaSyncState {
  lastSyncTimestamp: string | null;
  entityETags: Record<string, string>;
  syncToken: string | null;
  watermarks: Record<string, SyncWatermark>;
}

export interface SyncWatermark {
  lastSyncedId: string;
  lastSyncedTime: string;
}

export interface DeltaSyncHeaders {
  'If-Modified-Since'?: string;
  'If-None-Match'?: string;
  'X-Sync-Token'?: string;
  'X-Entity-Checksums'?: string;
}

export const DELTA_SYNC_STORAGE_KEY = 'pos_delta_sync_state';

// ----------------------------------------------------------------
// Callback & Batch Types
// ----------------------------------------------------------------

export type SyncCallback = (
  result: SyncResult,
  context: SyncContext
) => void | Promise<void>;
export type ConnectionChangeCallback = (status: ConnectionStatus) => void;
export type ConflictCallback = (conflict: Conflict) => void;
export type ErrorCallback = (error: SyncErrorInfo) => void;

export interface CallbackOptions {
  priority?: 'HIGH' | 'NORMAL' | 'LOW';
  filter?: CallbackFilter;
  once?: boolean;
}

export interface CallbackFilter {
  syncTypes?: SyncType[];
  onSuccess?: boolean;
  onFailure?: boolean;
  entityTypes?: string[];
}

export interface Batch {
  index: number;
  transactions: SyncTransaction[];
  size: number;
  estimatedSize: number;
  timeout: number;
}

export interface BatchResult {
  success: boolean;
  successful: { id: string; serverId: string; syncedAt: string }[];
  failed: { id: string; error: string }[];
  conflicts: { id: string; reason: string }[];
}

export interface ServerUpdates {
  products?: { created: unknown[]; updated: unknown[]; deleted: string[] };
  prices?: { created: unknown[]; updated: unknown[]; deleted: string[] };
  stock?: { created: unknown[]; updated: unknown[]; deleted: string[] };
  customers?: { created: unknown[]; updated: unknown[]; deleted: string[] };
}

export interface SyncTransaction {
  id: string;
  type: string;
  timestamp: string;
  data: unknown;
  status: 'PENDING' | 'SYNCED' | 'ERROR' | 'CONFLICT';
  signature?: string;
}

// ----------------------------------------------------------------
// Constants
// ----------------------------------------------------------------

// Sync Engine Constants
export const PUSH_ENDPOINT = '/api/sync/push-transactions/';
export const PULL_ENDPOINT = '/api/sync/pull-updates/';
export const HEALTH_PING_ENDPOINT = '/api/health/ping';
export const DEFAULT_BATCH_SIZE = 50;
export const MAX_BATCH_SIZE = 100;
export const MAX_PAYLOAD_SIZE = 5_000_000; // 5MB
export const SYNC_TIMEOUT = 120_000; // 120s
export const SYNC_LOCK_TIMEOUT = 300_000; // 5min
export const AUTO_SYNC_INTERVAL = 300_000; // 5min
export const MIN_SYNC_COOLDOWN = 60_000; // 60s
export const CONNECTION_CHECK_INTERVAL_OFFLINE = 30_000; // 30s
export const CONNECTION_CHECK_INTERVAL_ONLINE = 300_000; // 5min

// Connection Monitor Constants
export const PING_TIMEOUT = 5_000; // 5s
export const PING_RETRY_COUNT = 2;
export const PING_RETRY_INTERVAL = 500; // 500ms
export const LATENCY_THRESHOLD_SLOW = 2_000; // 2s
export const LATENCY_THRESHOLD_NORMAL = 500; // 500ms
export const CONNECTION_DEBOUNCE_DELAY = 2_000; // 2s

// Conflict Resolver Constants
export const PRICE_CHANGE_THRESHOLD_AUTO = 0.05; // 5%
export const PRICE_CHANGE_THRESHOLD_MANUAL = 0.15; // 15%
export const PRICE_IMPACT_THRESHOLD = 100.0; // $100
export const STOCK_RESERVATION_BUFFER = 0;
export const MANUAL_RESOLUTION_TIMEOUT = 86_400_000; // 24h
export const MANUAL_RESOLUTION_FIRST_REMINDER = 3_600_000; // 1h
export const MANUAL_RESOLUTION_ESCALATION_TIME = 14_400_000; // 4h

// Analytics Constants
export const AVERAGE_SYNC_DURATION_BASELINE = 15_000; // 15s
export const AVERAGE_SYNC_DURATION_THRESHOLD = 30_000; // 30s
export const SUCCESS_RATE_BASELINE = 0.98; // 98%
export const SUCCESS_RATE_THRESHOLD = 0.9; // 90%
export const NETWORK_ERROR_RATE_BASELINE = 0.02; // 2%
export const NETWORK_ERROR_RATE_THRESHOLD = 0.1; // 10%
export const HIGH_CONFLICT_RATE = 0.5;
export const ANALYTICS_RETENTION_DAYS = 90;

// Default Config
export const DEFAULT_SYNC_ENGINE_CONFIG: SyncEngineConfig = {
  apiEndpoint: '/api/sync',
  syncInterval: AUTO_SYNC_INTERVAL,
  maxRetryAttempts: 5,
  batchSize: DEFAULT_BATCH_SIZE,
  requestTimeout: 45_000,
  pushTimeout: 30_000,
  pullTimeout: 45_000,
  minSyncCooldown: MIN_SYNC_COOLDOWN,
  autoSyncEnabled: true,
  backgroundSyncEnabled: true,
};

export const DEFAULT_BACKOFF_CONFIG: BackoffConfig = {
  initialDelay: 1_000,
  maxDelay: 60_000,
  multiplier: 2,
  maxAttempts: 5,
  jitterFactor: 0.1,
  resetOnSuccess: true,
};
