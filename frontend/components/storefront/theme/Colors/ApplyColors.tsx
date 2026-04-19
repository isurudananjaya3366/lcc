'use client';

/**
 * Apply theme colors to CSS custom properties on :root.
 */

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';

function applyColorVariable(name: string, value: string) {
  document.documentElement.style.setProperty(name, value);
}

export function applyAllColors(colors: {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
}) {
  applyColorVariable('--theme-color-primary', colors.primary);
  applyColorVariable('--theme-color-secondary', colors.secondary);
  applyColorVariable('--theme-color-accent', colors.accent);
  applyColorVariable('--theme-color-background', colors.background);
  applyColorVariable('--theme-color-text-primary', colors.text);
}

interface ApplyColorsProps {
  className?: string;
}

export function ApplyColors({ className }: ApplyColorsProps) {
  const { colors } = useTheme();

  const handleApply = useCallback(() => {
    if (!colors) return;
    applyAllColors({
      primary: colors.primary,
      secondary: colors.secondary,
      accent: colors.accent,
      background: colors.background,
      text: colors.text.primary,
    });
  }, [colors]);

  return (
    <button
      type="button"
      onClick={handleApply}
      className={`rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50 ${className ?? ''}`}
      disabled={!colors}
    >
      Apply Colors
    </button>
  );
}
