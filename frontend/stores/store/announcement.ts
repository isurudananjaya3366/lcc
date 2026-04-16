'use client';

import { createStore } from '../utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface AnnouncementStoreState {
  isDismissed: boolean;
  dismissedAt: number | null;

  dismiss: () => void;
  reset: () => void;
  shouldShow: (expiryDays?: number) => boolean;
}

// ─── Store ──────────────────────────────────────────────────────────────────

const DAYS_MS = 24 * 60 * 60 * 1000;

export const useAnnouncementStore = createStore<AnnouncementStoreState>(
  'Announcement',
  (set, get) => ({
    isDismissed: false,
    dismissedAt: null,

    dismiss: () => {
      set((state) => {
        state.isDismissed = true;
        state.dismissedAt = Date.now();
      });
    },

    reset: () => {
      set((state) => {
        state.isDismissed = false;
        state.dismissedAt = null;
      });
    },

    shouldShow: (expiryDays = 30) => {
      const { isDismissed, dismissedAt } = get();

      if (!isDismissed) return true;
      if (!dismissedAt) return false;

      const daysSinceDismissal = (Date.now() - dismissedAt) / DAYS_MS;
      if (daysSinceDismissal > expiryDays) {
        // Auto-reset: expiry period has passed
        get().reset();
        return true;
      }

      return false;
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-announcement-bar',
      partialize: (state) => ({
        isDismissed: state.isDismissed,
        dismissedAt: state.dismissedAt,
      }),
    },
  }
);
