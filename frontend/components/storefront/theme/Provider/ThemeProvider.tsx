'use client';

// ================================================================
// Theme Provider
// ================================================================
// Wraps the storefront with theme context, loads theme from API,
// manages state, and injects CSS variables.
// ================================================================

import { useState, useEffect, useCallback, useMemo, type ReactNode } from 'react';
import { ThemeContext } from './ThemeContext';
import { CSSVariablesInjector } from './CSSVariablesInjector';
import type {
  Theme,
  PartialTheme,
  ThemeColors,
  ThemeFonts,
  ThemeLogo,
  ThemeHomepage,
} from '@/types/storefront/theme.types';
import { defaultTheme } from '@/styles/theme/defaults';
import { fetchTheme } from '@/services/storefront/themeService';
import { validateTheme } from '@/lib/theme/themeValidation';
import {
  getCachedTheme,
  getStaleCachedTheme,
  setCachedTheme,
  removeCachedTheme,
} from '@/lib/theme/themeCache';

// ─── Types ──────────────────────────────────────────────────────

interface ThemeProviderProps {
  children: ReactNode;
  tenantId?: string;
  initialTheme?: Theme;
  onThemeChange?: (theme: Theme) => void;
}

// ─── Constants ──────────────────────────────────────────────────

const MAX_RETRIES = 3;
const RETRY_DELAYS = [0, 1000, 3000];

// ─── Provider ───────────────────────────────────────────────────

export function ThemeProvider({
  children,
  tenantId = '',
  initialTheme,
  onThemeChange,
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme | null>(initialTheme ?? null);
  const [isLoading, setIsLoading] = useState(!initialTheme);
  const [error, setError] = useState<string | null>(null);

  // ── Theme Loader ────────────────────────────────────────────

  const loadTheme = useCallback(
    async (bypass = false) => {
      setIsLoading(true);
      setError(null);

      // Check cache first (unless bypassing)
      if (!bypass) {
        const cached = getCachedTheme(tenantId);
        if (cached) {
          setTheme(cached);
          setIsLoading(false);
          return;
        }
      }

      // Fetch from API with retry
      for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
        try {
          if ((RETRY_DELAYS[attempt] ?? 0) > 0) {
            await new Promise((r) => setTimeout(r, RETRY_DELAYS[attempt]));
          }

          const fetched = await fetchTheme(tenantId || undefined);
          const result = validateTheme(fetched);

          if (result.valid) {
            setTheme(fetched);
            setCachedTheme(tenantId, fetched);
            setIsLoading(false);
            return;
          }

          // Invalid shape — log and continue to fallback
          console.warn('[ThemeProvider] Fetched theme failed validation:', result);
        } catch (err) {
          if (attempt === MAX_RETRIES - 1) {
            console.error('[ThemeProvider] All fetch attempts failed:', err);
          }
        }
      }

      // All retries failed — try stale cache
      const stale = getStaleCachedTheme(tenantId);
      if (stale) {
        setTheme(stale);
        setError('Using cached theme (API unavailable)');
      } else {
        setTheme({ ...defaultTheme, tenantId });
        setError('Using default theme (API unavailable)');
      }

      setIsLoading(false);
    },
    [tenantId]
  );

  // Load on mount
  useEffect(() => {
    if (!initialTheme) {
      loadTheme();
    }
  }, [initialTheme, loadTheme]);

  // ── Update Theme ────────────────────────────────────────────

  const updateTheme = useCallback(
    async (updates: PartialTheme) => {
      if (!theme) return;

      const merged: Theme = {
        ...theme,
        ...updates,
        colors: updates.colors
          ? ({ ...theme.colors, ...updates.colors } as ThemeColors)
          : theme.colors,
        fonts: updates.fonts ? ({ ...theme.fonts, ...updates.fonts } as ThemeFonts) : theme.fonts,
        logo: updates.logo ? ({ ...theme.logo, ...updates.logo } as ThemeLogo) : theme.logo,
        homepage: updates.homepage
          ? ({ ...theme.homepage, ...updates.homepage } as ThemeHomepage)
          : theme.homepage,
        updatedAt: new Date().toISOString(),
      } as Theme;

      const result = validateTheme(merged);
      if (!result.valid) {
        setError('Invalid theme update');
        return;
      }

      setTheme(merged);
      setCachedTheme(tenantId, merged);
      onThemeChange?.(merged);
    },
    [theme, tenantId, onThemeChange]
  );

  // ── Reset Theme ─────────────────────────────────────────────

  const resetTheme = useCallback(async () => {
    const reset = { ...defaultTheme, tenantId };
    setTheme(reset);
    removeCachedTheme(tenantId);
    setError(null);
    onThemeChange?.(reset);
  }, [tenantId, onThemeChange]);

  // ── Context Value ───────────────────────────────────────────

  const contextValue = useMemo(
    () => ({
      theme,
      updateTheme,
      resetTheme,
      isLoading,
      error,
    }),
    [theme, updateTheme, resetTheme, isLoading, error]
  );

  return (
    <ThemeContext.Provider value={contextValue}>
      <CSSVariablesInjector theme={theme} />
      {children}
    </ThemeContext.Provider>
  );
}
