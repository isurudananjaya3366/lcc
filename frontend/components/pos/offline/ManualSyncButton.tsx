// ================================================================
// ManualSyncButton — Task 81
// ================================================================

'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useManualSync } from '@/hooks/useManualSync';
import { useOfflineStatus } from '@/hooks/useOfflineStatus';

type Variant = 'primary' | 'secondary' | 'icon';

interface ManualSyncButtonProps {
  variant?: Variant;
  className?: string;
}

const SYNC_OPTIONS = [
  {
    key: 'push' as const,
    label: 'Push Local Changes',
    icon: '⬆️',
    danger: false,
  },
  {
    key: 'pull' as const,
    label: 'Pull Server Updates',
    icon: '⬇️',
    danger: false,
  },
  { key: 'full' as const, label: 'Full Sync', icon: '🔄', danger: false },
  { key: 'forcePush' as const, label: 'Force Push', icon: '⚡', danger: true },
  {
    key: 'resetSync' as const,
    label: 'Reset Sync State',
    icon: '🗑️',
    danger: true,
  },
];

export function ManualSyncButton({
  variant = 'primary',
  className = '',
}: ManualSyncButtonProps) {
  const { trigger, loading, progress, lastResult, error } = useManualSync();
  const { isOnline } = useOfflineStatus();
  const [open, setOpen] = useState(false);
  const [confirm, setConfirm] = useState<(typeof SYNC_OPTIONS)[0] | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Keyboard shortcut: Ctrl+Shift+S
  const handleKeyboard = useCallback(
    (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        if (isOnline && !loading) trigger('full');
      }
    },
    [isOnline, loading, trigger]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyboard);
    return () => document.removeEventListener('keydown', handleKeyboard);
  }, [handleKeyboard]);

  const handleAction = (option: (typeof SYNC_OPTIONS)[0]) => {
    if (!isOnline) return;
    if (option.danger) {
      setConfirm(option);
      setOpen(false);
    } else {
      setOpen(false);
      trigger(option.key);
    }
  };

  const confirmAction = () => {
    if (confirm) {
      trigger(confirm.key);
      setConfirm(null);
    }
  };

  // Base button styles per variant
  const base =
    variant === 'primary'
      ? 'px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50'
      : variant === 'secondary'
        ? 'px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50'
        : 'p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50';

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef}>
      {/* Main button */}
      <button
        type="button"
        disabled={loading || !isOnline}
        onClick={() => setOpen(!open)}
        className={`${base} flex items-center gap-2 text-sm font-medium`}
        aria-haspopup="menu"
        aria-expanded={open}
        title={
          !isOnline
            ? 'Sync unavailable while offline'
            : 'Sync options (Ctrl+Shift+S)'
        }
      >
        {loading ? (
          <span className="animate-spin">⟳</span>
        ) : lastResult?.success ? (
          <span className="animate-bounce">✓</span>
        ) : error ? (
          <span>⚠</span>
        ) : (
          <span>🔄</span>
        )}
        {variant !== 'icon' && (loading ? `Syncing ${progress}%` : 'Sync')}
      </button>

      {/* Dropdown menu */}
      {open && !loading && (
        <div
          className="absolute right-0 mt-1 w-56 bg-white dark:bg-gray-900 border dark:border-gray-700 rounded-lg shadow-lg z-50"
          role="menu"
        >
          {SYNC_OPTIONS.map((option) => (
            <button
              key={option.key}
              type="button"
              onClick={() => handleAction(option)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 flex items-center gap-2 ${
                option.danger
                  ? 'text-red-600 dark:text-red-400'
                  : 'text-gray-700 dark:text-gray-300'
              }`}
              role="menuitem"
            >
              <span>{option.icon}</span>
              {option.label}
            </button>
          ))}
        </div>
      )}

      {/* Confirmation dialog */}
      {confirm && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
          role="dialog"
          aria-modal="true"
        >
          <div className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-xl max-w-sm w-full mx-4">
            <h3 className="font-semibold text-lg mb-2">
              Confirm {confirm.label}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              This action may overwrite data. Are you sure?
            </p>
            <div className="flex gap-2 justify-end">
              <button
                type="button"
                onClick={() => setConfirm(null)}
                className="px-3 py-1.5 border rounded text-sm dark:border-gray-600 dark:text-gray-300"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={confirmAction}
                className="px-3 py-1.5 bg-red-600 text-white rounded text-sm hover:bg-red-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
