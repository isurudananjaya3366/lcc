/**
 * Store Color Tokens
 *
 * Semantic color token system for the storefront.
 * Maps to CSS variables defined in styles/store.css.
 */

/** Primary brand palette (green for LankaCommerce) */
export const primaryColors = {
  50: '#f0fdf4',
  100: '#dcfce7',
  200: '#bbf7d0',
  300: '#86efac',
  400: '#4ade80',
  500: '#22c55e',
  600: '#16a34a',
  700: '#15803d',
  800: '#166534',
  900: '#14532d',
  950: '#052e16',
} as const;

/** Secondary/accent palette */
export const secondaryColors = {
  50: '#fff7ed',
  100: '#ffedd5',
  200: '#fed7aa',
  300: '#fdba74',
  400: '#fb923c',
  500: '#f97316',
  600: '#ea580c',
  700: '#c2410c',
  800: '#9a3412',
  900: '#7c2d12',
  950: '#431407',
} as const;

/** Semantic color tokens */
export const semanticColors = {
  success: {
    light: '#16a34a',
    dark: '#4ade80',
    bg: '#f0fdf4',
    border: '#86efac',
  },
  error: {
    light: '#dc2626',
    dark: '#f87171',
    bg: '#fef2f2',
    border: '#fca5a5',
  },
  warning: {
    light: '#d97706',
    dark: '#fbbf24',
    bg: '#fffbeb',
    border: '#fcd34d',
  },
  info: {
    light: '#2563eb',
    dark: '#60a5fa',
    bg: '#eff6ff',
    border: '#93c5fd',
  },
} as const;

/** UI-specific color tokens */
export const uiColors = {
  bgPage: { light: '#ffffff', dark: '#0a0a0a' },
  bgCard: { light: '#ffffff', dark: '#1a1a1a' },
  bgElevated: { light: '#f9fafb', dark: '#262626' },
  textPrimary: { light: '#171717', dark: '#fafafa' },
  textSecondary: { light: '#4b5563', dark: '#9ca3af' },
  textMuted: { light: '#6b7280', dark: '#6b7280' },
  borderDefault: { light: '#e5e7eb', dark: '#374151' },
  borderHover: { light: '#d1d5db', dark: '#4b5563' },
} as const;

/** Store color tokens for Tailwind CSS extension */
export const storeColorTokens = {
  'store-primary': primaryColors,
  'store-secondary': secondaryColors,
  'store-success': semanticColors.success.light,
  'store-error': semanticColors.error.light,
  'store-warning': semanticColors.warning.light,
  'store-info': semanticColors.info.light,
} as const;
