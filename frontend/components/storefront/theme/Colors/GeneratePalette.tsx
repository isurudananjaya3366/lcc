'use client';

/**
 * Auto-generate lighter and darker shades from a base hex color.
 */

import { useMemo } from 'react';
import { ColorSwatchPreview } from './ColorSwatchPreview';

// ─── Hex ↔ RGB helpers ──────────────────────────────────────────

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

function rgbToHex(r: number, g: number, b: number): string {
  const clamp = (v: number) => Math.max(0, Math.min(255, Math.round(v)));
  return '#' + [clamp(r), clamp(g), clamp(b)].map((c) => c.toString(16).padStart(2, '0')).join('');
}

// ─── HSL helpers ────────────────────────────────────────────────

function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255;
  g /= 255;
  b /= 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;
  if (max === min) return [0, 0, l];
  const d = max - min;
  const s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
  let h = 0;
  if (max === r) h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
  else if (max === g) h = ((b - r) / d + 2) / 6;
  else h = ((r - g) / d + 4) / 6;
  return [h, s, l];
}

function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  if (s === 0) {
    const v = Math.round(l * 255);
    return [v, v, v];
  }
  const hue2rgb = (p: number, q: number, t: number) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  return [
    Math.round(hue2rgb(p, q, h + 1 / 3) * 255),
    Math.round(hue2rgb(p, q, h) * 255),
    Math.round(hue2rgb(p, q, h - 1 / 3) * 255),
  ];
}

// ─── Palette Generation ─────────────────────────────────────────

export interface PaletteShade {
  label: string;
  hex: string;
  lightness: number;
}

/**
 * Generate 9 shades (50‑900) from a base hex color.
 */
export function generatePalette(baseHex: string): PaletteShade[] {
  const [r, g, b] = hexToRgb(baseHex);
  const [h, s] = rgbToHsl(r, g, b);

  const lightnessSteps = [0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2];
  const labels = ['50', '100', '200', '300', '400', '500', '600', '700', '800'];

  return lightnessSteps.map((l, i) => {
    const [rr, gg, bb] = hslToRgb(h, s, l);
    return {
      label: labels[i] ?? '',
      hex: rgbToHex(rr, gg, bb),
      lightness: Math.round(l * 100),
    };
  });
}

// ─── Component ──────────────────────────────────────────────────

interface GeneratePaletteProps {
  baseColor: string;
  label?: string;
}

export function GeneratePalette({ baseColor, label = 'Generated Palette' }: GeneratePaletteProps) {
  const shades = useMemo(() => generatePalette(baseColor), [baseColor]);

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-gray-700">{label}</h4>
      <div className="flex gap-1 overflow-x-auto">
        {shades.map((shade) => (
          <div key={shade.label} className="flex flex-col items-center gap-1">
            <ColorSwatchPreview color={shade.hex} size="sm" />
            <span className="text-[10px] text-gray-500">{shade.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
