// ================================================================
// useCacheWarmup — Task 34
// ================================================================
// React hook that drives the cache warmup flow after login.
// ================================================================

'use client';

import { useCallback, useRef, useState } from 'react';
import {
  warmupManager,
  type WarmupProgress,
} from '@/lib/offline/warmup-manager';

export function useCacheWarmup() {
  const [progress, setProgress] = useState<WarmupProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const running = useRef(false);

  const startWarmup = useCallback(async (terminalId: string) => {
    if (running.current) return;
    running.current = true;
    setError(null);

    try {
      const result = await warmupManager.startWarmup(terminalId, (p) =>
        setProgress(p)
      );
      setProgress(result);
    } catch (err) {
      setError(String(err));
    } finally {
      running.current = false;
    }
  }, []);

  const cancelWarmup = useCallback(() => {
    warmupManager.cancelWarmup();
  }, []);

  return { progress, error, startWarmup, cancelWarmup };
}
