// ================================================================
// ToastContainer — Task 82
// ================================================================
// Renders sync toast notifications to the DOM.
// ================================================================

'use client';

import React, { useEffect, useRef } from 'react';
import { useSyncToasts } from '@/hooks/useSyncToasts';

type ToastType =
  | 'success'
  | 'error'
  | 'warning'
  | 'info'
  | 'connection_lost'
  | 'connection_restored';

interface ToastItem {
  id: string;
  type: ToastType;
  title: string;
  message: string;
  dismissible: boolean;
  actions?: { label: string; onClick: () => void }[];
}

const TOAST_STYLES: Record<
  ToastType,
  { bg: string; border: string; icon: string; iconColor: string }
> = {
  success: {
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-300 dark:border-green-700',
    icon: '✓',
    iconColor: 'text-green-600',
  },
  error: {
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-300 dark:border-red-700',
    icon: '✗',
    iconColor: 'text-red-600',
  },
  warning: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/30',
    border: 'border-yellow-300 dark:border-yellow-700',
    icon: '⚠',
    iconColor: 'text-yellow-600',
  },
  info: {
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-300 dark:border-blue-700',
    icon: 'ℹ',
    iconColor: 'text-blue-600',
  },
  connection_lost: {
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-300 dark:border-red-700',
    icon: '⚡',
    iconColor: 'text-red-600',
  },
  connection_restored: {
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-300 dark:border-green-700',
    icon: '↻',
    iconColor: 'text-green-600',
  },
};

interface ToastContainerProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

export function ToastContainer({
  position = 'top-right',
}: ToastContainerProps) {
  const { toasts, dismiss } = useSyncToasts();
  const listRef = useRef<HTMLDivElement>(null);

  const posClass =
    position === 'top-right'
      ? 'top-4 right-4'
      : position === 'top-left'
        ? 'top-4 left-4'
        : position === 'bottom-right'
          ? 'bottom-4 right-4'
          : 'bottom-4 left-4';

  // Focus management: announce new toasts
  useEffect(() => {
    if (toasts.length > 0 && listRef.current) {
      const last = listRef.current.lastElementChild as HTMLElement | null;
      last?.focus();
    }
  }, [toasts.length]);

  if (toasts.length === 0) return null;

  return (
    <div
      ref={listRef}
      className={`fixed ${posClass} z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none`}
      role="region"
      aria-label="Notifications"
      aria-live="polite"
    >
      {toasts.map((toast: ToastItem) => {
        const style = TOAST_STYLES[toast.type];
        return (
          <div
            key={toast.id}
            className={`${style.bg} ${style.border} border rounded-lg shadow-lg p-4 pointer-events-auto animate-in slide-in-from-right transition-all`}
            role="alert"
            tabIndex={-1}
          >
            <div className="flex items-start gap-3">
              <span
                className={`${style.iconColor} text-lg flex-shrink-0`}
                aria-hidden="true"
              >
                {style.icon}
              </span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-gray-900 dark:text-white">
                  {toast.title}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-0.5">
                  {toast.message}
                </p>
                {toast.actions && toast.actions.length > 0 && (
                  <div className="flex gap-2 mt-2">
                    {toast.actions.map((action, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={action.onClick}
                        className="text-xs font-medium underline text-blue-600 dark:text-blue-400 hover:text-blue-800"
                      >
                        {action.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              {toast.dismissible && (
                <button
                  type="button"
                  onClick={() => dismiss(toast.id)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-lg leading-none"
                  aria-label="Dismiss notification"
                >
                  ×
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
