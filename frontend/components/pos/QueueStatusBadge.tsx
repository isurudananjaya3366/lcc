// ================================================================
// QueueStatusBadge — Task 51
// ================================================================
// Compact badge showing pending/failed transaction counts.
// ================================================================

'use client';

import React from 'react';
import type { QueueStatusSummary } from '@/lib/offline/queue-types';

interface QueueStatusBadgeProps {
  status: QueueStatusSummary | null;
  className?: string;
}

export function QueueStatusBadge({
  status,
  className = '',
}: QueueStatusBadgeProps) {
  if (!status || (status.pending === 0 && status.failed === 0)) {
    return null;
  }

  const hasFailed = status.failed > 0;
  const label = hasFailed
    ? `${status.pending} pending, ${status.failed} failed`
    : `${status.pending} pending`;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
        hasFailed
          ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
          : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
      } ${className}`}
      role="status"
      aria-label={`Transaction queue: ${label}`}
    >
      <span
        className={`inline-block h-1.5 w-1.5 rounded-full ${
          hasFailed ? 'bg-red-500' : 'bg-yellow-500'
        }`}
      />
      {label}
    </span>
  );
}
