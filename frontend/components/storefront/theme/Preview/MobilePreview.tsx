'use client';

// ================================================================
// Mobile Preview (Task 84)
// ================================================================
// Mobile viewport preview with phone frame bezel styling.
// ================================================================

import React from 'react';
import { cn } from '@/lib/utils';
import { PreviewFrame } from './PreviewFrame';

// ─── Types ──────────────────────────────────────────────────────

export interface MobilePreviewProps {
  className?: string;
  onLoad?: () => void;
}

// ─── Component ──────────────────────────────────────────────────

export function MobilePreview({ className, onLoad }: MobilePreviewProps) {
  return (
    <div className={cn('flex h-full w-full items-start justify-center py-4', className)}>
      {/* Phone frame bezel */}
      <div className="relative rounded-[2.5rem] border-[6px] border-gray-800 bg-gray-800 shadow-xl">
        {/* Notch */}
        <div className="absolute left-1/2 top-0 z-10 h-6 w-28 -translate-x-1/2 rounded-b-2xl bg-gray-800" />

        {/* Status bar area */}
        <div className="flex items-center justify-between rounded-t-[2rem] bg-white px-6 pb-1 pt-7 text-[10px] text-gray-500">
          <span>9:41</span>
          <div className="flex items-center gap-1">
            <span>●●●</span>
            <span>WiFi</span>
            <span>🔋</span>
          </div>
        </div>

        {/* Preview content */}
        <div className="overflow-hidden" style={{ width: '375px', height: '667px' }}>
          <PreviewFrame viewport="mobile" onLoad={onLoad} />
        </div>

        {/* Home indicator */}
        <div className="flex justify-center rounded-b-[2rem] bg-white py-2">
          <div className="h-1 w-28 rounded-full bg-gray-300" />
        </div>
      </div>
    </div>
  );
}
