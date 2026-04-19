'use client';

// ================================================================
// Preview Refresh (Task 85)
// ================================================================
// Refresh button to manually reload the preview iframe.
// ================================================================

import React from 'react';
import { RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

// ─── Types ──────────────────────────────────────────────────────

export interface PreviewRefreshProps {
  onRefresh: () => void;
  loading?: boolean;
  disabled?: boolean;
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────

export function PreviewRefresh({
  onRefresh,
  loading = false,
  disabled = false,
  className,
}: PreviewRefreshProps) {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={onRefresh}
      disabled={disabled || loading}
      aria-label="Refresh preview"
      title="Refresh Preview"
      className={cn(className)}
    >
      <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
    </Button>
  );
}
