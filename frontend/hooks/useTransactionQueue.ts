// ================================================================
// useTransactionQueue — Task 51
// ================================================================
// React hook wrapping the TransactionQueue for component use.
// ================================================================

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { TransactionQueue } from '@/lib/offline/transaction-queue';
import type {
  QueueNotification,
  QueueStatusSummary,
} from '@/lib/offline/queue-types';

export function useTransactionQueue() {
  const queueRef = useRef<TransactionQueue | null>(null);
  const [status, setStatus] = useState<QueueStatusSummary | null>(null);
  const [notifications, setNotifications] = useState<QueueNotification[]>([]);

  useEffect(() => {
    const queue = new TransactionQueue();
    queueRef.current = queue;

    const unsubscribe = queue.addNotificationListener((n) => {
      setNotifications((prev) => [n, ...prev].slice(0, 50));
    });

    queue.initialize().then(() => queue.getQueueStatus().then(setStatus));

    return () => {
      unsubscribe();
      queue.destroy();
    };
  }, []);

  const refreshStatus = useCallback(async () => {
    if (queueRef.current) {
      setStatus(await queueRef.current.getQueueStatus());
    }
  }, []);

  const dismissNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  return {
    queue: queueRef.current,
    status,
    notifications,
    refreshStatus,
    dismissNotification,
  };
}
