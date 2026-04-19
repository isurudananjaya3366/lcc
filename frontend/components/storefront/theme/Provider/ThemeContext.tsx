'use client';

// ================================================================
// Theme Context
// ================================================================
// React Context for theme management.
// ================================================================

import { createContext, useContext } from 'react';
import type { ThemeContextValue } from '@/types/storefront/theme.types';

// ─── Default Context Value ──────────────────────────────────────

const defaultContextValue: ThemeContextValue = {
  theme: null,
  updateTheme: async () => {},
  resetTheme: async () => {},
  isLoading: false,
  error: null,
};

// ─── Context ────────────────────────────────────────────────────

export const ThemeContext = createContext<ThemeContextValue>(defaultContextValue);
ThemeContext.displayName = 'ThemeContext';

// ─── Internal Hook ──────────────────────────────────────────────

export function useThemeContext(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return context;
}
