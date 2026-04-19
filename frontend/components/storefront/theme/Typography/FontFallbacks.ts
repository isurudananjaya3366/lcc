// ================================================================
// Font Fallback Stacks
// ================================================================
// System font stacks per category used as fallbacks when a
// Google Font is unavailable or still loading.
// ================================================================

import type { FontCategory } from './FontList';

export const fontFallbacks: Record<FontCategory, string> = {
  'sans-serif':
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
  serif: "Georgia, 'Times New Roman', Times, serif",
  display: "Impact, 'Arial Black', sans-serif",
  monospace: "Consolas, Monaco, 'Courier New', monospace",
};

export function buildFontStack(fontFamily: string, category: FontCategory): string {
  const fallback = fontFallbacks[category];
  const name = fontFamily.includes("'") ? fontFamily : `'${fontFamily}'`;
  return `${name}, ${fallback}`;
}

export function getFallbackStack(category: FontCategory): string {
  return fontFallbacks[category];
}
