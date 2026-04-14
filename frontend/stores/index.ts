// ================================================================
// Zustand State Stores — Barrel Export
// ================================================================
// Global state management using Zustand.
// No providers needed — import and use directly in components.
//
// Import: import { useAuthStore, useUIStore } from '@/stores'
// ================================================================

// ── Types ──────────────────────────────────────────────────────
export type {
  BaseStore,
  StateSlice,
  ActionSlice,
  Store,
  PersistConfig,
  DevToolsConfig,
  CreateStoreOptions,
  ThemeMode,
  NotificationType,
  NotificationAction,
  Notification,
  Modal,
  User,
  Tenant,
  TenantSettings,
} from './types';

// ── Utilities ──────────────────────────────────────────────────
export {
  createStore,
  isClient,
  getPersistConfig,
  registerStoreReset,
  resetAllStores,
  useHydration,
  useShallow,
} from './utils';

// ── Stores ─────────────────────────────────────────────────────
export { useUIStore } from './useUIStore';
export { useAuthStore } from './useAuthStore';
// export { useCartStore } from './useCartStore'
// export { usePOSStore } from './usePOSStore'
// export { useFilterStore } from './useFilterStore'
