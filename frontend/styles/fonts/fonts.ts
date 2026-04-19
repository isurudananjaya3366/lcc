/**
 * Font Configuration — next/font setup
 *
 * Self-hosted Google Fonts via next/font for zero layout shift.
 * Fonts are loaded at build time — no external requests at runtime.
 */

import { Inter, Playfair_Display } from 'next/font/google';

// ── Primary Font (Body) ─────────────────────────────────────────

export const primaryFont = Inter({
  subsets: ['latin'],
  display: 'swap',
  weight: ['400', '500', '600', '700'],
  variable: '--font-body',
  preload: true,
  fallback: ['system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
});

// ── Heading Font ────────────────────────────────────────────────

export const headingFont = Playfair_Display({
  subsets: ['latin'],
  display: 'swap',
  weight: ['400', '600', '700'],
  variable: '--font-heading',
  preload: true,
  fallback: ['Georgia', 'Times New Roman', 'serif'],
});

// ── Font Class Names (applied to <html> or <body>) ─────────────

export const fontVariableClasses = `${primaryFont.variable} ${headingFont.variable}`;
