'use client';

// ================================================================
// CSS Variables Injector
// ================================================================
// Injects theme values as CSS custom properties on :root.
// ================================================================

import { useEffect } from 'react';
import type { Theme } from '@/types/storefront/theme.types';

// ─── CSS Variable Mapping ───────────────────────────────────────

function getThemeCSSVariables(theme: Theme): Record<string, string> {
  return {
    // Colors
    '--theme-color-primary': theme.colors.primary,
    '--theme-color-secondary': theme.colors.secondary,
    '--theme-color-accent': theme.colors.accent,
    '--theme-color-background': theme.colors.background,
    '--theme-color-surface': theme.colors.surface,

    // Text colors
    '--theme-color-text-primary': theme.colors.text.primary,
    '--theme-color-text-secondary': theme.colors.text.secondary,
    '--theme-color-text-disabled': theme.colors.text.disabled,

    // Border colors
    '--theme-color-border-light': theme.colors.border.light,
    '--theme-color-border-dark': theme.colors.border.dark,

    // Status colors
    '--theme-color-success': theme.colors.status.success,
    '--theme-color-warning': theme.colors.status.warning,
    '--theme-color-error': theme.colors.status.error,
    '--theme-color-info': theme.colors.status.info,

    // Fonts
    '--theme-font-heading': theme.fonts.heading,
    '--theme-font-body': theme.fonts.body,
    '--theme-font-scale': String(theme.fonts.scale),

    // Font weights
    '--theme-font-weight-light': String(theme.fonts.weights.light),
    '--theme-font-weight-normal': String(theme.fonts.weights.normal),
    '--theme-font-weight-medium': String(theme.fonts.weights.medium),
    '--theme-font-weight-bold': String(theme.fonts.weights.bold),

    // Logo dimensions
    '--theme-logo-width': `${theme.logo.width}px`,
    '--theme-logo-height': `${theme.logo.height}px`,
  };
}

// ─── Component ──────────────────────────────────────────────────

interface CSSVariablesInjectorProps {
  theme: Theme | null;
}

export function CSSVariablesInjector({ theme }: CSSVariablesInjectorProps) {
  useEffect(() => {
    if (!theme) return;

    const variables = getThemeCSSVariables(theme);
    const root = document.documentElement;

    for (const [property, value] of Object.entries(variables)) {
      root.style.setProperty(property, value);
    }

    return () => {
      for (const property of Object.keys(variables)) {
        root.style.removeProperty(property);
      }
    };
  }, [theme]);

  return null;
}
