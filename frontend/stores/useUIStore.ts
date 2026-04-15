/**
 * UI State Store
 *
 * Centralised Zustand store for all UI-related state:
 *   - Sidebar collapse / active menu
 *   - Theme (light / dark / system)
 *   - Modal registry
 *   - Notification queue
 *   - Command palette visibility
 *
 * Persisted fields: `isCollapsed`, `theme`
 * Transient fields: modals, notifications, commandPaletteOpen
 */

'use client';

import { createStore, registerStoreReset } from './utils';
import type { ThemeMode, Notification, NotificationType, Modal } from './types';

// ── Default durations per notification type (ms) ───────────────

const DEFAULT_DURATIONS: Record<NotificationType, number> = {
  success: 3000,
  error: 5000,
  warning: 4000,
  info: 3000,
};

const MAX_NOTIFICATIONS = 5;

// ── Interfaces ─────────────────────────────────────────────────

interface UIState {
  // Sidebar
  isCollapsed: boolean;
  activeMenu: string | null;
  // Theme
  theme: ThemeMode;
  // Modals
  modals: Map<string, Modal>;
  // Notifications
  notifications: Notification[];
  // Command Palette
  commandPaletteOpen: boolean;
}

interface UIActions {
  // Sidebar
  toggleSidebar: () => void;
  setActiveMenu: (menuId: string | null) => void;
  // Theme
  setTheme: (mode: ThemeMode) => void;
  // Modals
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  openModal: <T = any>(modalId: string, props?: T) => void;
  closeModal: (modalId: string) => void;
  closeAllModals: () => void;
  // Notifications
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  // Command Palette
  toggleCommandPalette: () => void;
  // Reset
  reset: () => void;
}

type UIStore = UIState & UIActions;

// ── Initial state ──────────────────────────────────────────────

const initialState: UIState = {
  isCollapsed: false,
  activeMenu: null,
  theme: 'system',
  modals: new Map(),
  notifications: [],
  commandPaletteOpen: false,
};

// ── Simple ID generator (avoids extra dependency) ──────────────

let _idCounter = 0;
function generateId(): string {
  _idCounter += 1;
  return `notif_${Date.now()}_${_idCounter}`;
}

// ── Timeout tracker ────────────────────────────────────────────

const timeoutMap = new Map<string, ReturnType<typeof setTimeout>>();

// ── Store ──────────────────────────────────────────────────────

export const useUIStore = createStore<UIStore>(
  'UI',
  (set, get) => ({
    ...initialState,

    // ── Sidebar Actions ──────────────────────────────────────

    toggleSidebar: () =>
      set((state) => {
        state.isCollapsed = !state.isCollapsed;
      }),

    setActiveMenu: (menuId) =>
      set((state) => {
        state.activeMenu = menuId;
      }),

    // ── Theme Actions ────────────────────────────────────────

    setTheme: (mode) =>
      set((state) => {
        state.theme = mode;
      }),

    // ── Modal Actions ────────────────────────────────────────

    openModal: (modalId, props) =>
      set((state) => {
        state.modals.set(modalId, {
          id: modalId,
          isOpen: true,
          props: props as Record<string, unknown> | undefined,
        });
      }),

    closeModal: (modalId) =>
      set((state) => {
        state.modals.delete(modalId);
      }),

    closeAllModals: () =>
      set((state) => {
        state.modals.clear();
      }),

    // ── Notification Actions ─────────────────────────────────

    addNotification: (notification) => {
      const id = generateId();
      const duration = notification.duration ?? DEFAULT_DURATIONS[notification.type];

      set((state) => {
        const entry: Notification = {
          ...notification,
          id,
          timestamp: new Date(),
          duration,
        };
        state.notifications.unshift(entry);

        // Cap at MAX_NOTIFICATIONS
        if (state.notifications.length > MAX_NOTIFICATIONS) {
          const removed = state.notifications.splice(MAX_NOTIFICATIONS);
          // Clear timeouts for evicted notifications
          for (const r of removed) {
            const t = timeoutMap.get(r.id);
            if (t) {
              clearTimeout(t);
              timeoutMap.delete(r.id);
            }
          }
        }
      });

      // Auto-dismiss
      if (duration !== undefined && duration > 0) {
        const timeout = setTimeout(() => {
          get().removeNotification(id);
        }, duration);
        timeoutMap.set(id, timeout);
      }

      return id;
    },

    removeNotification: (id) => {
      const t = timeoutMap.get(id);
      if (t) {
        clearTimeout(t);
        timeoutMap.delete(id);
      }
      set((state) => {
        state.notifications = state.notifications.filter((n) => n.id !== id);
      });
    },

    clearNotifications: () => {
      // Clear all pending timeouts
      for (const [, t] of timeoutMap) {
        clearTimeout(t);
      }
      timeoutMap.clear();

      set((state) => {
        state.notifications = [];
      });
    },

    // ── Command Palette Actions ──────────────────────────────

    toggleCommandPalette: () =>
      set((state) => {
        state.commandPaletteOpen = !state.commandPaletteOpen;
      }),

    // ── Reset ────────────────────────────────────────────────

    reset: () => {
      // Clear all pending notification timeouts
      for (const [, t] of timeoutMap) {
        clearTimeout(t);
      }
      timeoutMap.clear();

      set(initialState);
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-ui',
      version: 1,
      partialize: (state: UIStore) => ({
        isCollapsed: state.isCollapsed,
        theme: state.theme,
      }),
    },
  }
);

// Register for global resetAllStores()
registerStoreReset(() => useUIStore.getState().reset());
