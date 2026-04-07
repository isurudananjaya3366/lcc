// ================================================================
// Offline Module — Barrel Export
// ================================================================

// Core services
export { idbService } from './indexeddb';
export { cacheService } from './cache-service';
export { cacheManager } from './cache-manager';
export { versioningService } from './versioning';
export { syncManager } from './sync-manager';
export { warmupManager } from './warmup-manager';

// Service worker utilities
export {
  registerServiceWorker,
  checkServiceWorkerSupport,
  checkForUpdates,
  skipWaiting,
  unregisterServiceWorker,
} from './service-worker';

// Object stores
export {
  productsService,
  categoriesService,
  customersService,
  settingsService,
  transactionsService,
} from './stores';

// Schema & types
export {
  DATABASE_NAME,
  DATABASE_VERSION,
  ObjectStoreNames,
  type Product,
  type ProductVariant,
  type Category,
  type Customer,
  type Transaction,
  type TransactionItem,
  type Setting,
  type SyncMeta,
} from './schema';

// Utilities
export * from './utils';

// Transaction queue
export { TransactionQueue } from './transaction-queue';
export {
  generateOfflineTransactionId,
  isValidOfflineId,
  parseOfflineId,
} from './id-generator';
export * from './queue-types';

// Sync engine (Group D)
export {
  SyncEngine,
  BackoffStrategy,
  SyncError,
  syncEngine,
} from './sync-engine';
export { ConnectionMonitor, connectionMonitor } from './connection-monitor';
export { ConflictResolver, conflictResolver } from './conflict-resolver';
export { SyncAnalytics, syncAnalytics } from './sync-analytics';
export * from './sync-types';
