'use client';

// ================================================================
// Google Fonts Integration
// ================================================================
// Dynamically loads Google Fonts by injecting <link> tags.
// ================================================================

import { useEffect, useRef, useCallback } from 'react';
import type { FontDefinition } from './FontList';

const loadedFonts = new Set<string>();

function buildGoogleFontsUrl(fontName: string, weights: number[]): string {
  const family = fontName.replace(/ /g, '+');
  const wghts = weights.join(';');
  return `https://fonts.googleapis.com/css2?family=${family}:wght@${wghts}&display=swap`;
}

function ensurePreconnect() {
  if (typeof document === 'undefined') return;
  const id = '__gf_preconnect';
  if (document.getElementById(id)) return;

  const apis = document.createElement('link');
  apis.id = id;
  apis.rel = 'preconnect';
  apis.href = 'https://fonts.googleapis.com';
  document.head.appendChild(apis);

  const static_ = document.createElement('link');
  static_.rel = 'preconnect';
  static_.href = 'https://fonts.gstatic.com';
  static_.crossOrigin = 'anonymous';
  document.head.appendChild(static_);
}

export function loadGoogleFont(
  fontName: string,
  weights: number[] = [400, 500, 600, 700]
): Promise<void> {
  if (typeof document === 'undefined') return Promise.resolve();
  if (loadedFonts.has(fontName)) return Promise.resolve();

  ensurePreconnect();

  return new Promise<void>((resolve, reject) => {
    const url = buildGoogleFontsUrl(fontName, weights);
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    link.dataset.font = fontName;

    link.onload = () => {
      loadedFonts.add(fontName);
      resolve();
    };
    link.onerror = () => reject(new Error(`Failed to load font: ${fontName}`));

    document.head.appendChild(link);
  });
}

export function isFontLoaded(fontName: string): boolean {
  return loadedFonts.has(fontName);
}

export function loadMultipleFonts(fonts: { name: string; weights?: number[] }[]): Promise<void[]> {
  return Promise.all(fonts.map((f) => loadGoogleFont(f.name, f.weights)));
}

// ─── React wrapper ──────────────────────────────────────────────

interface GoogleFontsIntegrationProps {
  fonts: FontDefinition[];
  onLoaded?: () => void;
  onError?: (err: Error) => void;
}

export function GoogleFontsIntegration({ fonts, onLoaded, onError }: GoogleFontsIntegrationProps) {
  const loaded = useRef(false);

  const load = useCallback(async () => {
    if (loaded.current) return;
    loaded.current = true;
    try {
      await loadMultipleFonts(fonts.map((f) => ({ name: f.name, weights: f.weights })));
      onLoaded?.();
    } catch (err) {
      onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }, [fonts, onLoaded, onError]);

  useEffect(() => {
    void load();
  }, [load]);

  return null;
}
