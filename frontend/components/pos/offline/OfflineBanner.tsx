// ================================================================
// OfflineBanner — Task 78
// ================================================================

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { useOfflineStatus } from '@/hooks/useOfflineStatus';
import { usePendingCount } from '@/hooks/usePendingCount';

interface OfflineBannerProps {
  show?: boolean;
  position?: 'top' | 'bottom';
  dismissible?: boolean;
  showActions?: boolean;
  onDismiss?: () => void;
  onRetry?: () => void;
  onViewPending?: () => void;
  className?: string;
  message?: string;
}

const SESSION_KEY = 'pos_offline_banner_dismissed';

export function OfflineBanner({
  show: showOverride,
  position = 'top',
  dismissible = true,
  showActions = true,
  onDismiss,
  onRetry,
  onViewPending,
  className = '',
  message = 'You are currently offline. Transactions will be saved locally and synced when connection is restored.',
}: OfflineBannerProps) {
  const { isOnline, status, lastSyncTime } = useOfflineStatus();
  const { total: pendingCount } = usePendingCount();
  const [dismissed, setDismissed] = useState(false);

  // Restore dismissed state from sessionStorage
  useEffect(() => {
    try {
      setDismissed(sessionStorage.getItem(SESSION_KEY) === 'true');
    } catch {
      /* sessionStorage may be unavailable */
    }
  }, []);

  // Re-show when status changes (e.g., went from online → offline)
  useEffect(() => {
    if (!isOnline) {
      setDismissed(false);
      try {
        sessionStorage.removeItem(SESSION_KEY);
      } catch {
        /* noop */
      }
    }
  }, [isOnline]);

  const handleDismiss = useCallback(() => {
    setDismissed(true);
    try {
      sessionStorage.setItem(SESSION_KEY, 'true');
    } catch {
      /* noop */
    }
    onDismiss?.();
  }, [onDismiss]);

  const visible = showOverride ?? !isOnline;
  if (!visible || dismissed) return null;

  const posClass = position === 'top' ? 'top-0' : 'bottom-0';

  // Status-specific messages
  const statusMsg =
    status === 'SYNC_ERROR'
      ? 'Sync failed. Some changes may not be saved to the server.'
      : message;

  const lastSyncFmt = lastSyncTime
    ? `Last sync: ${lastSyncTime.toLocaleTimeString()}`
    : null;

  return (
    <div
      className={`fixed ${posClass} left-0 right-0 z-40 bg-amber-50 dark:bg-amber-900/80 border-b border-amber-200 dark:border-amber-800 px-4 py-3 transition-transform duration-300 animate-in slide-in-from-top ${className}`}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-center justify-between gap-4 max-w-7xl mx-auto flex-wrap sm:flex-nowrap">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span
            className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0"
            aria-hidden="true"
          >
            ⚠️
          </span>
          <div className="flex flex-col">
            <p className="text-sm text-amber-800 dark:text-amber-100">
              {statusMsg}
            </p>
            <p className="text-xs text-amber-600 dark:text-amber-300">
              {pendingCount != null && pendingCount > 0 && (
                <span>
                  {pendingCount} pending transaction
                  {pendingCount > 1 ? 's' : ''} ·{' '}
                </span>
              )}
              {lastSyncFmt && <span>{lastSyncFmt}</span>}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {showActions && (
            <>
              {onRetry && (
                <button
                  type="button"
                  onClick={onRetry}
                  className="text-xs font-medium px-2 py-1 rounded bg-amber-200 dark:bg-amber-700 text-amber-900 dark:text-amber-100 hover:bg-amber-300 dark:hover:bg-amber-600"
                >
                  Retry Connection
                </button>
              )}
              {onViewPending && pendingCount != null && pendingCount > 0 && (
                <button
                  type="button"
                  onClick={onViewPending}
                  className="text-xs font-medium px-2 py-1 rounded bg-amber-200 dark:bg-amber-700 text-amber-900 dark:text-amber-100 hover:bg-amber-300 dark:hover:bg-amber-600"
                >
                  View Pending
                </button>
              )}
            </>
          )}
          {dismissible && (
            <button
              type="button"
              onClick={handleDismiss}
              className="w-5 h-5 flex items-center justify-center hover:bg-amber-100 dark:hover:bg-amber-800 rounded cursor-pointer text-amber-600 dark:text-amber-300"
              aria-label="Dismiss offline notice"
            >
              ✕
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
