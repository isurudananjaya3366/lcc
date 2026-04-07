// ================================================================
// SyncStatusBar + PendingTransactionBadge — Tasks 75-76
// ================================================================

'use client';

import React from 'react';

// ----------------------------------------------------------------
// PendingTransactionBadge
// ----------------------------------------------------------------

interface PendingTransactionBadgeProps {
  count: number;
  showCount?: boolean;
  variant?: 'default' | 'minimal' | 'detailed';
  size?: 'small' | 'medium' | 'large';
  className?: string;
  onClick?: () => void;
}

function badgeColor(count: number): string {
  if (count === 0)
    return 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400';
  if (count <= 10)
    return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400';
  if (count <= 50)
    return 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400';
  return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400';
}

const BADGE_SIZE = {
  small: 'text-xs',
  medium: 'text-sm',
  large: 'text-base',
} as const;

export function PendingTransactionBadge({
  count,
  showCount = true,
  variant = 'default',
  size = 'medium',
  className = '',
  onClick,
}: PendingTransactionBadgeProps) {
  const display = count > 99 ? '99+' : String(count);

  if (variant === 'minimal') {
    return (
      <span
        className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${badgeColor(count)} ${className}`}
        role="status"
        aria-label={`${count} pending transactions`}
        onClick={onClick}
      >
        {showCount ? display : ''}
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 border rounded-full ${BADGE_SIZE[size]} font-medium ${badgeColor(count)} ${className}`}
      role="status"
      aria-label={`${count} pending transactions`}
      onClick={onClick}
    >
      {showCount && display}
      {variant === 'detailed' && (
        <span className="text-xs opacity-75">pending</span>
      )}
    </span>
  );
}

// ----------------------------------------------------------------
// SyncStatusBar
// ----------------------------------------------------------------

type SyncState = 'idle' | 'syncing' | 'complete' | 'error';

interface SyncStatusBarProps {
  state?: SyncState;
  percentage?: number;
  currentEntity?: string | null;
  pendingCount?: number;
  position?: 'top' | 'bottom' | 'floating';
  compact?: boolean;
  className?: string;
}

const STATE_TEXT: Record<SyncState, string> = {
  idle: 'Idle',
  syncing: 'Syncing...',
  complete: 'Sync complete',
  error: 'Sync error',
};

const STATE_COLOR: Record<SyncState, string> = {
  idle: 'text-gray-600 dark:text-gray-400',
  syncing: 'text-blue-600 dark:text-blue-400',
  complete: 'text-green-600 dark:text-green-400',
  error: 'text-red-600 dark:text-red-400',
};

const POSITION_CLASS: Record<string, string> = {
  top: 'fixed top-0 left-0 right-0 z-40',
  bottom: 'fixed bottom-0 left-0 right-0 z-40',
  floating: 'fixed bottom-4 right-4 w-80 z-40 rounded-lg',
};

export function SyncStatusBar({
  state = 'idle',
  percentage = 0,
  currentEntity,
  pendingCount = 0,
  position = 'top',
  compact = false,
  className = '',
}: SyncStatusBarProps) {
  if (state === 'idle' && pendingCount === 0) return null;

  return (
    <div
      className={`bg-white dark:bg-gray-900 shadow-sm border-b dark:border-gray-700 ${POSITION_CLASS[position]} ${className}`}
      role="status"
      aria-label="Sync status"
      aria-live="polite"
    >
      {/* Progress bar rail */}
      {state === 'syncing' && (
        <div className="h-1 bg-gray-200 dark:bg-gray-700">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all"
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
      )}

      <div
        className={`flex items-center justify-between ${compact ? 'px-3 py-1' : 'px-4 py-2'}`}
      >
        {/* Left: status */}
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${STATE_COLOR[state]}`}>
            {state === 'syncing' && (
              <span className="inline-block animate-spin mr-1">⟳</span>
            )}
            {STATE_TEXT[state]}
          </span>
          {currentEntity && state === 'syncing' && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              — {currentEntity}
            </span>
          )}
        </div>

        {/* Center: percentage */}
        {state === 'syncing' && (
          <span className="text-xs font-mono text-blue-600 dark:text-blue-400">
            {percentage}%
          </span>
        )}

        {/* Right: pending badge */}
        <PendingTransactionBadge count={pendingCount} size="small" />
      </div>
    </div>
  );
}
