'use client';

// ================================================================
// Font Loader – Dynamic font loading utility
// ================================================================
// Loads fonts on demand and fires callbacks when ready.
// ================================================================

import { useEffect, useState, useCallback } from 'react';
import { loadGoogleFont, isFontLoaded } from './GoogleFontsIntegration';
import type { FontDefinition } from './FontList';

export type FontLoadStatus = 'idle' | 'loading' | 'loaded' | 'error';

interface UseFontLoaderResult {
  status: FontLoadStatus;
  load: (font: FontDefinition) => Promise<void>;
}

export function useFontLoader(onLoad?: () => void): UseFontLoaderResult {
  const [status, setStatus] = useState<FontLoadStatus>('idle');

  const load = useCallback(
    async (font: FontDefinition) => {
      if (isFontLoaded(font.name)) {
        setStatus('loaded');
        onLoad?.();
        return;
      }
      setStatus('loading');
      try {
        await loadGoogleFont(font.name, font.weights);
        setStatus('loaded');
        onLoad?.();
      } catch {
        setStatus('error');
      }
    },
    [onLoad]
  );

  return { status, load };
}

// ─── Component wrapper ─────────────────────────────────────────

interface FontLoaderProps {
  font: FontDefinition | null;
  onLoad?: () => void;
  onError?: (err: Error) => void;
  children?: React.ReactNode;
}

export function FontLoader({ font, onLoad, onError, children }: FontLoaderProps) {
  const [status, setStatus] = useState<FontLoadStatus>('idle');

  useEffect(() => {
    if (!font) return;
    if (isFontLoaded(font.name)) {
      setStatus('loaded');
      onLoad?.();
      return;
    }

    let cancelled = false;
    setStatus('loading');

    loadGoogleFont(font.name, font.weights)
      .then(() => {
        if (!cancelled) {
          setStatus('loaded');
          onLoad?.();
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setStatus('error');
          onError?.(err instanceof Error ? err : new Error(String(err)));
        }
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [font?.name]);

  if (!font) return <>{children}</>;

  return <div data-font-status={status}>{children}</div>;
}
