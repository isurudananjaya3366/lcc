'use client';

import { WifiOff, Wifi, Loader2, X } from 'lucide-react';
import { useState } from 'react';
import { useOfflineStatus } from '@/hooks/useOfflineStatus';

export function OfflineIndicator() {
  const { isOnline, isSyncing } = useOfflineStatus();
  const [dismissed, setDismissed] = useState(false);

  // Online — no banner needed
  if (isOnline && !isSyncing) return null;

  if (isSyncing) {
    return (
      <div className="flex items-center justify-center gap-2 bg-yellow-50 px-4 py-1.5 text-xs text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200">
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        <span>Syncing pending transactions...</span>
      </div>
    );
  }

  if (dismissed) {
    return (
      <div className="flex items-center justify-end bg-red-50 px-4 py-1 dark:bg-red-900/30">
        <div className="flex items-center gap-1 text-xs text-red-600 dark:text-red-400">
          <WifiOff className="h-3 w-3" />
          <span>Offline</span>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex items-center justify-between bg-red-50 px-4 py-2 dark:bg-red-900/30"
      role="alert"
    >
      <div className="flex items-center gap-2 text-sm text-red-800 dark:text-red-200">
        <WifiOff className="h-4 w-4 shrink-0" />
        <span>
          <strong>No internet connection</strong> — Working offline. Some features are unavailable.
          Sales will sync when connection is restored.
        </span>
      </div>
      <button
        onClick={() => setDismissed(true)}
        className="ml-4 rounded p-1 text-red-600 hover:bg-red-100 dark:text-red-400 dark:hover:bg-red-900/50"
        aria-label="Dismiss offline warning"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
