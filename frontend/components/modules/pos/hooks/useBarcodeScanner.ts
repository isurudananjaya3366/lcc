'use client';

import { useRef, useCallback, useEffect } from 'react';

const BARCODE_TIMEOUT_MS = 100;
const MIN_BARCODE_LENGTH = 6;
const MAX_BARCODE_LENGTH = 13;
const MAX_KEYSTROKE_GAP_MS = 50;
const BARCODE_PATTERN = /^[a-zA-Z0-9]+$/;

/**
 * Detects barcode scanner input by measuring keystroke timing.
 * Scanners send characters rapidly (< 50ms gap) ending with Enter.
 */
export function useBarcodeScanner(onScan: (barcode: string) => void) {
  const bufferRef = useRef('');
  const lastKeystrokeRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const resetBuffer = useCallback(() => {
    bufferRef.current = '';
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if focused on an input (search box handles its own input)
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

      const now = Date.now();
      const gap = now - lastKeystrokeRef.current;
      lastKeystrokeRef.current = now;

      // Clear timeout
      if (timerRef.current) clearTimeout(timerRef.current);

      if (e.key === 'Enter') {
        const barcode = bufferRef.current;
        if (
          barcode.length >= MIN_BARCODE_LENGTH &&
          barcode.length <= MAX_BARCODE_LENGTH &&
          BARCODE_PATTERN.test(barcode)
        ) {
          e.preventDefault();
          onScan(barcode);
        }
        resetBuffer();
        return;
      }

      // Single printable character
      if (e.key.length !== 1) return;

      // If gap is too long, start new buffer
      if (gap > MAX_KEYSTROKE_GAP_MS && bufferRef.current.length > 0) {
        resetBuffer();
      }

      bufferRef.current += e.key;

      // Auto-clear buffer after timeout
      timerRef.current = setTimeout(resetBuffer, BARCODE_TIMEOUT_MS);
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [onScan, resetBuffer]);
}
