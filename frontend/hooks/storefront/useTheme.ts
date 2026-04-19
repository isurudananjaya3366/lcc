'use client';

// ================================================================
// useTheme Hook
// ================================================================
// Convenient hook for accessing theme data and operations.
// ================================================================

import { useThemeContext } from '@/components/storefront/theme/Provider/ThemeContext';
import type {
  Theme,
  ThemeColors,
  ThemeFonts,
  ThemeLogo,
  ThemeHomepage,
  PartialTheme,
} from '@/types/storefront/theme.types';

// ─── Return Type ────────────────────────────────────────────────

export interface UseThemeReturn {
  theme: Theme | null;
  colors: ThemeColors | null;
  fonts: ThemeFonts | null;
  logo: ThemeLogo | null;
  homepage: ThemeHomepage | null;
  updateTheme: (updates: PartialTheme) => Promise<void>;
  resetTheme: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
  isThemeReady: boolean;
  getColor: (name: string) => string;
  getFont: (type: 'heading' | 'body') => string;
  getFontWeight: (weight: 'light' | 'normal' | 'medium' | 'bold') => number;
}

// ─── Color Accessor ─────────────────────────────────────────────

const FALLBACK_COLOR = '#000000';

function buildGetColor(colors: ThemeColors | null) {
  return (name: string): string => {
    if (!colors) return FALLBACK_COLOR;

    const colorMap: Record<string, string> = {
      primary: colors.primary,
      secondary: colors.secondary,
      accent: colors.accent,
      background: colors.background,
      surface: colors.surface,
      'text-primary': colors.text.primary,
      'text-secondary': colors.text.secondary,
      'text-disabled': colors.text.disabled,
      'border-light': colors.border.light,
      'border-dark': colors.border.dark,
      success: colors.status.success,
      warning: colors.status.warning,
      error: colors.status.error,
      info: colors.status.info,
    };

    return colorMap[name] ?? FALLBACK_COLOR;
  };
}

// ─── Hook ───────────────────────────────────────────────────────

export function useTheme(): UseThemeReturn {
  const { theme, updateTheme, resetTheme, isLoading, error } = useThemeContext();

  const colors = theme?.colors ?? null;
  const fonts = theme?.fonts ?? null;
  const logo = theme?.logo ?? null;
  const homepage = theme?.homepage ?? null;
  const isThemeReady = !isLoading && theme !== null;

  const getColor = buildGetColor(colors);

  const getFont = (type: 'heading' | 'body'): string => {
    if (!fonts) return 'system-ui, sans-serif';
    return fonts[type];
  };

  const getFontWeight = (weight: 'light' | 'normal' | 'medium' | 'bold'): number => {
    if (!fonts) return 400;
    return fonts.weights[weight];
  };

  return {
    theme,
    colors,
    fonts,
    logo,
    homepage,
    updateTheme,
    resetTheme,
    isLoading,
    error,
    isThemeReady,
    getColor,
    getFont,
    getFontWeight,
  };
}
