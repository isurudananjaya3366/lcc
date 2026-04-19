'use client';

// ================================================================
// Theme Zustand Store
// ================================================================
// Zustand store for theme state with Immer + DevTools.
// ================================================================

import { createStore } from '../utils';
import type { ThemeStoreState, PartialTheme, Theme } from '@/types/storefront/theme.types';

// ─── Initial State ──────────────────────────────────────────────

type ThemeStoreActions = Pick<
  ThemeStoreState,
  'setTheme' | 'updateTheme' | 'resetTheme' | 'setLoading' | 'setError'
>;

const initialState: Omit<ThemeStoreState, keyof ThemeStoreActions> = {
  theme: null,
  isLoading: false,
  error: null,
};

// ─── Store ──────────────────────────────────────────────────────

export const useThemeStore = createStore<ThemeStoreState>(
  'Theme',
  (set) => ({
    ...initialState,

    setTheme: (theme: Theme) => {
      set((state) => {
        state.theme = theme;
        state.error = null;
      });
    },

    updateTheme: (updates: PartialTheme) => {
      set((state) => {
        if (!state.theme) return;

        if (updates.colors) {
          Object.assign(state.theme.colors, updates.colors);
        }
        if (updates.fonts) {
          Object.assign(state.theme.fonts, updates.fonts);
        }
        if (updates.logo) {
          Object.assign(state.theme.logo, updates.logo);
        }
        if (updates.homepage) {
          Object.assign(state.theme.homepage, updates.homepage);
        }
        if (updates.name !== undefined) {
          state.theme.name = updates.name;
        }
        if (updates.isActive !== undefined) {
          state.theme.isActive = updates.isActive;
        }
        state.theme.updatedAt = new Date().toISOString();
      });
    },

    resetTheme: (defaultTheme: Theme) => {
      set((state) => {
        state.theme = defaultTheme;
        state.error = null;
      });
    },

    setLoading: (loading: boolean) => {
      set((state) => {
        state.isLoading = loading;
      });
    },

    setError: (error: string | null) => {
      set((state) => {
        state.error = error;
      });
    },
  }),
  {
    persist: true,
    persistConfig: {
      name: 'lcc-theme',
      version: 1,
      partialize: (state: ThemeStoreState) => ({
        theme: state.theme,
      }),
    },
  }
);
