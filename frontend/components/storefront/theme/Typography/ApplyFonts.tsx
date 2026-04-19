'use client';

// ================================================================
// Apply Fonts – Apply font CSS variables to :root
// ================================================================

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { getFontByName } from './FontList';
import { buildFontStack } from './FontFallbacks';

export interface TypographyConfig {
  headingFont: string;
  bodyFont: string;
  fontSize: number;
  lineHeight: number;
  headingWeight: number;
  bodyWeight: number;
}

function setVar(name: string, value: string) {
  document.documentElement.style.setProperty(name, value);
}

export function applyTypography(config: TypographyConfig) {
  if (typeof document === 'undefined') return;

  const headingDef = getFontByName(config.headingFont);
  const bodyDef = getFontByName(config.bodyFont);

  const headingStack = headingDef
    ? buildFontStack(headingDef.name, headingDef.category)
    : `'${config.headingFont}', sans-serif`;

  const bodyStack = bodyDef
    ? buildFontStack(bodyDef.name, bodyDef.category)
    : `'${config.bodyFont}', sans-serif`;

  const base = config.fontSize;

  requestAnimationFrame(() => {
    setVar('--font-heading', headingStack);
    setVar('--font-body', bodyStack);
    setVar('--font-size-base', `${base}px`);
    setVar('--font-size-sm', `${base * 0.875}px`);
    setVar('--font-size-lg', `${base * 1.125}px`);
    setVar('--font-size-xl', `${base * 1.25}px`);
    setVar('--font-size-2xl', `${base * 1.5}px`);
    setVar('--font-size-3xl', `${base * 1.875}px`);
    setVar('--font-size-4xl', `${base * 2.25}px`);
    setVar('--line-height-base', String(config.lineHeight));
    setVar('--line-height-heading', String(config.lineHeight - 0.3));
    setVar('--line-height-tight', String(config.lineHeight - 0.25));
    setVar('--font-weight-heading', String(config.headingWeight));
    setVar('--font-weight-body', String(config.bodyWeight));
  });
}

// ─── React component ────────────────────────────────────────────

interface ApplyFontsProps {
  config: TypographyConfig;
  className?: string;
}

export function ApplyFonts({ config, className }: ApplyFontsProps) {
  const { updateTheme } = useTheme();

  const handleApply = useCallback(() => {
    applyTypography(config);
    void updateTheme({
      fonts: {
        heading: config.headingFont,
        body: config.bodyFont,
        scale: config.fontSize / 16,
        weights: {
          light: 300,
          normal: config.bodyWeight,
          medium: Math.min(config.bodyWeight + 100, 700),
          bold: config.headingWeight,
        },
      },
    });
  }, [config, updateTheme]);

  return (
    <button
      type="button"
      onClick={handleApply}
      className={`rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors ${className ?? ''}`}
    >
      Apply Typography
    </button>
  );
}
