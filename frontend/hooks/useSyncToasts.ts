// ================================================================
// useSyncToasts — Task 82
// ================================================================

'use client';

import { useCallback, useRef, useState } from 'react';

type ToastType =
  | 'success'
  | 'error'
  | 'warning'
  | 'info'
  | 'connection_lost'
  | 'connection_restored';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message: string;
  duration: number;
  dismissible: boolean;
  actions?: { label: string; onClick: () => void }[];
}

const MAX_TOASTS = 3;
let nextId = 0;

const TEMPLATES: Record<
  ToastType,
  Pick<Toast, 'title' | 'duration' | 'dismissible'>
> = {
  success: { title: 'Sync Complete', duration: 3000, dismissible: true },
  error: { title: 'Sync Failed', duration: 8000, dismissible: true },
  warning: { title: 'Sync Warning', duration: 5000, dismissible: true },
  info: { title: 'Sync Info', duration: 4000, dismissible: true },
  connection_lost: {
    title: 'Connection Lost',
    duration: 0,
    dismissible: false,
  },
  connection_restored: {
    title: 'Connection Restored',
    duration: 3000,
    dismissible: true,
  },
};

export function useSyncToasts() {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const timersRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(
    new Map()
  );

  const dismiss = useCallback((id: string) => {
    const timer = timersRef.current.get(id);
    if (timer) {
      clearTimeout(timer);
      timersRef.current.delete(id);
    }
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const show = useCallback(
    (type: ToastType, message: string, actions?: Toast['actions']) => {
      const template = TEMPLATES[type];
      const id = `toast-${++nextId}`;
      const toast: Toast = { id, type, message, ...template, actions };

      setToasts((prev) => {
        const updated = [...prev, toast];
        return updated.slice(-MAX_TOASTS);
      });

      if (template.duration > 0) {
        timersRef.current.set(
          id,
          setTimeout(() => dismiss(id), template.duration)
        );
      }

      return id;
    },
    [dismiss]
  );

  const showSuccess = useCallback(
    (msg: string) => show('success', msg),
    [show]
  );
  const showError = useCallback(
    (msg: string, actions?: Toast['actions']) => show('error', msg, actions),
    [show]
  );
  const showWarning = useCallback(
    (msg: string) => show('warning', msg),
    [show]
  );
  const showInfo = useCallback((msg: string) => show('info', msg), [show]);
  const showConnectionLost = useCallback(
    () =>
      show(
        'connection_lost',
        'Offline mode activated. Changes will be queued.'
      ),
    [show]
  );
  const showConnectionRestored = useCallback(
    () =>
      show(
        'connection_restored',
        'Back online. Queued changes will sync automatically.'
      ),
    [show]
  );

  return {
    toasts,
    dismiss,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showConnectionLost,
    showConnectionRestored,
  };
}
