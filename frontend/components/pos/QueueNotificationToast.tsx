// ================================================================
// QueueNotificationToast — Task 51
// ================================================================
// Toast that displays queue notifications and auto-dismisses.
// ================================================================

'use client';

import React, { useEffect } from 'react';
import type { QueueNotification } from '@/lib/offline/queue-types';
import { NotificationSeverity } from '@/lib/offline/queue-types';

interface QueueNotificationToastProps {
  notification: QueueNotification;
  onDismiss: (id: string) => void;
  autoHideMs?: number;
}

const SEVERITY_STYLES: Record<NotificationSeverity, string> = {
  [NotificationSeverity.INFO]:
    'border-blue-300 bg-blue-50 text-blue-800 dark:border-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  [NotificationSeverity.WARNING]:
    'border-yellow-300 bg-yellow-50 text-yellow-800 dark:border-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300',
  [NotificationSeverity.ERROR]:
    'border-red-300 bg-red-50 text-red-800 dark:border-red-700 dark:bg-red-900/30 dark:text-red-300',
  [NotificationSeverity.SUCCESS]:
    'border-green-300 bg-green-50 text-green-800 dark:border-green-700 dark:bg-green-900/30 dark:text-green-300',
};

export function QueueNotificationToast({
  notification,
  onDismiss,
  autoHideMs = 5000,
}: QueueNotificationToastProps) {
  useEffect(() => {
    if (autoHideMs <= 0) return;
    const timer = setTimeout(() => onDismiss(notification.id), autoHideMs);
    return () => clearTimeout(timer);
  }, [notification.id, onDismiss, autoHideMs]);

  return (
    <div
      role="alert"
      className={`flex items-start gap-2 rounded-lg border p-3 shadow-sm ${SEVERITY_STYLES[notification.severity]}`}
    >
      <p className="flex-1 text-sm">{notification.message}</p>
      <button
        type="button"
        onClick={() => onDismiss(notification.id)}
        className="shrink-0 rounded p-0.5 opacity-60 hover:opacity-100"
        aria-label="Dismiss notification"
      >
        ✕
      </button>
    </div>
  );
}
