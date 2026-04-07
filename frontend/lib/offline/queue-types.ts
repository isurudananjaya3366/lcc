// ================================================================
// Transaction Queue Types — Tasks 35-52
// ================================================================
// All type definitions for the offline transaction queue.
// ================================================================

// ── Enums ──────────────────────────────────────────────────────

export enum TransactionStatus {
  PENDING = 'PENDING',
  SYNCING = 'SYNCING',
  SYNCED = 'SYNCED',
  FAILED = 'FAILED',
}

export enum OrderingStrategy {
  FIFO = 'FIFO',
  LIFO = 'LIFO',
  PRIORITY = 'PRIORITY',
  DEPENDENCY_AWARE = 'DEPENDENCY_AWARE',
}

export enum TransactionPriority {
  CRITICAL = 4,
  HIGH = 3,
  NORMAL = 2,
  LOW = 1,
}

export enum CleanupStrategy {
  AGE_BASED = 'AGE_BASED',
  COUNT_BASED = 'COUNT_BASED',
  STORAGE_BASED = 'STORAGE_BASED',
  MANUAL = 'MANUAL',
}

export enum NotificationType {
  TRANSACTION_QUEUED = 'TRANSACTION_QUEUED',
  TRANSACTION_SYNCED = 'TRANSACTION_SYNCED',
  TRANSACTION_FAILED = 'TRANSACTION_FAILED',
  QUEUE_SIZE_WARNING = 'QUEUE_SIZE_WARNING',
  DEPENDENCY_RESOLVED = 'DEPENDENCY_RESOLVED',
  SYNC_STARTED = 'SYNC_STARTED',
  SYNC_COMPLETED = 'SYNC_COMPLETED',
  EXPORT_COMPLETE = 'EXPORT_COMPLETE',
}

export enum NotificationSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  SUCCESS = 'SUCCESS',
}

// ── Payload Interfaces ─────────────────────────────────────────

export interface CartItem {
  product_id: string;
  quantity: number;
  price: number;
  subtotal: number;
}

export interface TransactionPayload {
  terminal_id: string;
  session_id: string;
  items: CartItem[];
  grand_total: number;
  payment_method: string;
  timestamp: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  customer_id?: string | null;
  customer_name?: string;
  customer_phone?: string;
  currency?: string;
}

// ── Queued Transaction ─────────────────────────────────────────

export interface ErrorDetails {
  error_code?: string;
  error_type?: string;
  request_id?: string;
  stack_trace?: string;
  retry_after?: number;
}

export interface QueuedTransaction {
  offline_id: string;
  terminal_id: string;
  session_id: string;
  created_at: string;
  synced_at: string | null;
  status: TransactionStatus;
  retry_count: number;
  error_message: string | null;
  depends_on: string | null;
  payload: TransactionPayload;
  position?: number;
  priority?: TransactionPriority;
  server_transaction_id?: string;
  last_error_at?: string;
  error_details?: ErrorDetails;
  next_retry_at?: string;
}

// ── Config & Metadata ──────────────────────────────────────────

export interface QueueConfig {
  maxRetries: number;
  retryDelays: number[];
  cleanupThreshold: number;
  batchSize: number;
  orderingStrategy: OrderingStrategy;
  cleanupStrategy: CleanupStrategy;
  maxSyncedTransactions: number;
  preserveSyncedDays: number;
  cleanupInterval: number;
}

export interface QueueMetadata {
  version: string;
  session_id: string;
  last_sync_attempt: string | null;
  last_successful_sync: string | null;
  clean_shutdown: boolean;
  configuration: QueueConfig;
  created_at: string;
  updated_at: string;
}

// ── Position Tracking ──────────────────────────────────────────

export interface PositionMetadata {
  position: number;
  totalPending: number;
  estimatedWait?: number | null;
}

export interface PendingTransactionWithDeps extends QueuedTransaction {
  position: number;
  dependency_status?: TransactionStatus;
}

// ── Status Summary ─────────────────────────────────────────────

export interface QueueStatusSummary {
  pending: number;
  syncing: number;
  synced: number;
  failed: number;
  total: number;
  oldest_pending: string | null;
  last_sync_attempt: string | null;
  last_successful_sync: string | null;
  average_retry_count: number;
  max_retry_count: number;
  at_max_retries: number;
  health_score: number;
  estimated_clear_time: number | null;
  oldest_pending_age: number | null;
  error_summary: {
    most_common_error: string | null;
    error_count: number;
    error_distribution?: Array<{ error: string; count: number }>;
  };
}

// ── Validation ─────────────────────────────────────────────────

export interface ValidationError {
  field: string;
  code: string;
  message: string;
  value?: unknown;
}

export interface ValidationWarning {
  field: string;
  code: string;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

// ── Export / Import ────────────────────────────────────────────

export interface ExportOptions {
  include_statuses?: TransactionStatus[];
  include_synced?: boolean;
  date_from?: string;
  date_to?: string;
  terminal_id?: string;
}

export interface QueueExportFile {
  export_version: string;
  schema_version: string;
  exported_at: string;
  terminal_id: string;
  session_id: string;
  configuration: QueueConfig;
  metadata: {
    transaction_count: number;
    included_statuses: string[];
    date_range: { from: string | null; to: string | null };
  };
  transactions: QueuedTransaction[];
  checksum: string;
}

// ── Dependency Graph ───────────────────────────────────────────

export interface DependencyGraph {
  nodes: Map<string, QueuedTransaction>;
  edges: Map<string, string[]>;
  roots: string[];
  leaves: string[];
}

export interface CircularDependency {
  transactions: string[];
  detected_at: string;
  resolution: 'MARK_FAILED' | 'MANUAL';
}

// ── Cleanup ────────────────────────────────────────────────────

export interface CleanupResult {
  total_scanned: number;
  removed: number;
  kept: number;
  freed_space?: number;
  duration_ms: number;
  strategy: CleanupStrategy;
  timestamp: string;
}

export interface IntegrityReport {
  total_checked: number;
  valid: number;
  invalid: number;
  warnings: number;
  invalid_transactions: Array<{
    offline_id: string;
    errors: ValidationError[];
  }>;
}

// ── Notifications ──────────────────────────────────────────────

export interface QueueNotification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  severity: NotificationSeverity;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

// ── Constants ──────────────────────────────────────────────────

export const DEFAULT_QUEUE_CONFIG: QueueConfig = {
  maxRetries: 5,
  retryDelays: [1000, 2000, 5000, 10000, 30000],
  cleanupThreshold: 86_400_000,
  batchSize: 10,
  orderingStrategy: OrderingStrategy.FIFO,
  cleanupStrategy: CleanupStrategy.AGE_BASED,
  maxSyncedTransactions: 1000,
  preserveSyncedDays: 1,
  cleanupInterval: 3_600_000,
};

export const VALIDATION_RULES = {
  MAX_ITEMS: 1000,
  MIN_GRAND_TOTAL: 0,
  MAX_GRAND_TOTAL: 10_000_000,
  MAX_ITEM_QUANTITY: 1000,
  MIN_TERMINAL_ID_LEN: 2,
  MAX_TERMINAL_ID_LEN: 10,
  ROUNDING_TOLERANCE: 0.01,
  TIMESTAMP_FUTURE_TOLERANCE_S: 300,
  TIMESTAMP_AGE_WARNING_S: 2_592_000,
} as const;

export const QUEUE_SIZE_THRESHOLDS = [10, 25, 50, 100] as const;
