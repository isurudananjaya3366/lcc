'use client';

// ================================================================
// Font Loading State – Indicator while fonts load
// ================================================================

import { Loader2 } from 'lucide-react';
import type { FontLoadStatus } from './FontLoader';

interface FontLoadingStateProps {
  status: FontLoadStatus;
  fontName?: string;
  className?: string;
}

export function FontLoadingState({ status, fontName, className }: FontLoadingStateProps) {
  if (status === 'idle' || status === 'loaded') return null;

  if (status === 'loading') {
    return (
      <div
        className={`inline-flex items-center gap-1.5 text-xs text-gray-500 ${className ?? ''}`}
        role="status"
        aria-live="polite"
      >
        <Loader2 className="h-3 w-3 animate-spin" />
        <span>Loading{fontName ? ` ${fontName}` : ''}…</span>
      </div>
    );
  }

  return (
    <div className={`text-xs text-red-500 ${className ?? ''}`} role="alert">
      Failed to load{fontName ? ` ${fontName}` : ' font'}
    </div>
  );
}
