'use client';

/**
 * WCAG contrast ratio calculation and accessibility check.
 */

import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

// ─── Relative Luminance ─────────────────────────────────────────

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

function sRGBtoLinear(channel: number): number {
  const c = channel / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function relativeLuminance(hex: string): number {
  const [r, g, b] = hexToRgb(hex);
  return 0.2126 * sRGBtoLinear(r) + 0.7152 * sRGBtoLinear(g) + 0.0722 * sRGBtoLinear(b);
}

// ─── Public helpers ─────────────────────────────────────────────

export function getContrastRatio(fg: string, bg: string): number {
  const l1 = relativeLuminance(fg);
  const l2 = relativeLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

export type WCAGLevel = 'AAA' | 'AA' | 'AA-Large' | 'Fail';

export function getWCAGLevel(ratio: number): WCAGLevel {
  if (ratio >= 7) return 'AAA';
  if (ratio >= 4.5) return 'AA';
  if (ratio >= 3) return 'AA-Large';
  return 'Fail';
}

// ─── Component ──────────────────────────────────────────────────

interface ContrastCheckProps {
  foreground: string;
  background: string;
  label?: string;
}

export function ContrastCheck({
  foreground,
  background,
  label = 'Contrast Check',
}: ContrastCheckProps) {
  const ratio = getContrastRatio(foreground, background);
  const level = getWCAGLevel(ratio);

  const Icon = level === 'Fail' ? XCircle : level === 'AA-Large' ? AlertTriangle : CheckCircle;

  const colorClass =
    level === 'Fail' ? 'text-red-600' : level === 'AA-Large' ? 'text-yellow-600' : 'text-green-600';

  const message =
    level === 'Fail'
      ? 'Fails WCAG — Not readable'
      : level === 'AA-Large'
        ? 'AA Large text only'
        : level === 'AA'
          ? 'AA — Good'
          : 'AAA — Excellent';

  return (
    <div className="space-y-2 rounded-lg border border-gray-200 p-3">
      <h4 className="text-sm font-semibold text-gray-700">{label}</h4>
      <div className="flex items-center gap-2">
        <Icon className={`h-5 w-5 ${colorClass}`} />
        <span className={`text-sm font-medium ${colorClass}`}>{ratio.toFixed(1)}:1</span>
        <span className="text-xs text-gray-500">{message}</span>
      </div>
      <div
        className="rounded p-3 text-sm"
        style={{ backgroundColor: background, color: foreground }}
      >
        Sample text — The quick brown fox jumps over the lazy dog.
      </div>
    </div>
  );
}
