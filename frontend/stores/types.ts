/**
 * Zustand Store Type Definitions
 *
 * Base interfaces and utility types used by all Zustand stores.
 * Follows the state-slice pattern: separate state, actions, and
 * a combined Store type.
 */

// ── Base Store Interface ───────────────────────────────────────

/** Every store must expose a `reset()` method */
export interface BaseStore {
  reset: () => void;
}

// ── Slice Pattern Types ────────────────────────────────────────

/** State-only slice (data, loading flags, errors) */
export interface StateSlice {
  [key: string]: unknown;
}

/** Action-only slice (methods that mutate state) */
export interface ActionSlice {
  [key: string]: ((...args: unknown[]) => void) | unknown;
}

/** Combined store = state + actions + base */
export type Store<S extends StateSlice, A extends ActionSlice> = S & A & BaseStore;

// ── Middleware Configuration Types ─────────────────────────────

export interface PersistConfig<T = unknown> {
  /** localStorage key — prefixed with `lcc-` by convention */
  name: string;
  /** Storage backend (default: localStorage) */
  storage?: Storage;
  /** Select which properties to persist */
  partialize?: (state: T) => Partial<T>;
  /** Schema version — bump when shape changes */
  version?: number;
  /** Callback invoked when state is rehydrated from storage */
  onRehydrateStorage?: (state: T) => ((state?: T | undefined, error?: unknown) => void) | void;
}

export interface DevToolsConfig {
  /** Store name shown in Redux DevTools */
  name: string;
  /** Enable/disable (default: development only) */
  enabled?: boolean;
}

// ── Store Option Types ─────────────────────────────────────────

export interface CreateStoreOptions<T = unknown> {
  /** Enable localStorage persistence */
  persist?: boolean;
  /** Persist configuration overrides */
  persistConfig?: PersistConfig<T>;
  /** Enable devtools (default: true in dev) */
  devtools?: boolean;
}

// ── Theme Types ────────────────────────────────────────────────

export type ThemeMode = 'light' | 'dark' | 'system';

// ── Notification Types ─────────────────────────────────────────

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface NotificationAction {
  label: string;
  onClick: () => void;
}

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  timestamp: Date;
  action?: NotificationAction;
}

// ── Modal Types ────────────────────────────────────────────────

export interface Modal {
  id: string;
  isOpen: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  props?: Record<string, any>;
}

// ── Auth Types ─────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  avatar: string | null;
}

export interface TenantSettings {
  logo: string;
  primaryColor: string;
  secondaryColor: string;
  enabledModules: string[];
  featureFlags: Record<string, boolean>;
  maxUsers: number;
  maxProducts: number;
  storageLimit: number;
  timezone: string;
  currency: string;
  language: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  plan: string;
  settings: TenantSettings;
}
