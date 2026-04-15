'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
  type FC,
} from 'react';
import type { StoreTheme, StoreThemeContextValue } from '@/types/store-theme';

const STORAGE_KEY = 'store-theme';

const StoreThemeContext = createContext<StoreThemeContextValue | null>(null);

export interface ThemeProviderProps {
  children: ReactNode;
  defaultTheme?: StoreTheme;
  storageKey?: string;
}

/**
 * Theme provider for the storefront — manages light/dark/auto modes.
 * Persists preference to localStorage and respects system preference.
 */
const ThemeProvider: FC<ThemeProviderProps> = ({
  children,
  defaultTheme = 'light',
  storageKey = STORAGE_KEY,
}) => {
  const [theme, setThemeState] = useState<StoreTheme>(defaultTheme);
  const [mounted, setMounted] = useState(false);

  // Resolve effective theme (light or dark) from 'auto' mode
  const resolveTheme = useCallback((t: StoreTheme): 'light' | 'dark' => {
    if (t === 'auto') {
      if (typeof window !== 'undefined') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return 'light';
    }
    return t;
  }, []);

  const isDark = resolveTheme(theme) === 'dark';
  const isLight = !isDark;

  // Initialize from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(storageKey);
      if (stored && ['light', 'dark', 'auto'].includes(stored)) {
        setThemeState(stored as StoreTheme);
      }
    } catch {
      // localStorage unavailable
    }
    setMounted(true);
  }, [storageKey]);

  // Apply theme to document root
  useEffect(() => {
    if (!mounted) return;
    const resolved = resolveTheme(theme);
    document.documentElement.setAttribute('data-store-theme', resolved);
    document.documentElement.classList.toggle('dark', resolved === 'dark');
  }, [theme, mounted, resolveTheme]);

  // Listen for system theme changes when in 'auto' mode
  useEffect(() => {
    if (theme !== 'auto') return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = () => {
      const resolved = mq.matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-store-theme', resolved);
      document.documentElement.classList.toggle('dark', resolved === 'dark');
    };
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [theme]);

  const setTheme = useCallback(
    (newTheme: StoreTheme) => {
      setThemeState(newTheme);
      try {
        localStorage.setItem(storageKey, newTheme);
      } catch {
        // localStorage quota exceeded
      }
    },
    [storageKey]
  );

  const toggleTheme = useCallback(() => {
    setTheme(isDark ? 'light' : 'dark');
  }, [isDark, setTheme]);

  const value: StoreThemeContextValue = {
    theme,
    setTheme,
    toggleTheme,
    isDark,
    isLight,
  };

  return <StoreThemeContext.Provider value={value}>{children}</StoreThemeContext.Provider>;
};

export function useStoreTheme(): StoreThemeContextValue {
  const ctx = useContext(StoreThemeContext);
  if (!ctx) {
    throw new Error('useStoreTheme must be used within a ThemeProvider');
  }
  return ctx;
}

export default ThemeProvider;
