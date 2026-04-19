'use client';

// ================================================================
// Desktop Preview (Task 83)
// ================================================================
// Full-width desktop viewport preview wrapper.
// ================================================================

import React from 'react';
import { cn } from '@/lib/utils';
import { PreviewFrame } from './PreviewFrame';

// ─── Types ──────────────────────────────────────────────────────

export interface DesktopPreviewProps {
  className?: string;
  onLoad?: () => void;
}

// ─── Component ──────────────────────────────────────────────────

export function DesktopPreview({ className, onLoad }: DesktopPreviewProps) {
  return (
    <div className={cn('h-full w-full min-w-[768px]', className)}>
      <PreviewFrame viewport="desktop" onLoad={onLoad} className="h-full w-full" />
    </div>
  );
}
