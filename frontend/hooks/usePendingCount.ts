// ================================================================
// usePendingCount — Task 76
// ================================================================
// Real-time pending transaction count hook.
// ================================================================

'use client';

import { useCallback, useEffect, useState } from 'react';

export interface PendingCountState {
  total: number;
  byStatus: {
    pending: number;
    failed: number;
    retrying: number;
  };
  loading: boolean;
}

const INITIAL: PendingCountState = {
  total: 0,
  byStatus: { pending: 0, failed: 0, retrying: 0 },
  loading: true,
};

const POLL_INTERVAL = 10_000; // 10s

export function usePendingCount() {
  const [state, setState] = useState<PendingCountState>(INITIAL);

  const refresh = useCallback(async () => {
    try {
      const { TransactionQueue } =
        await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();
      const status = await queue.getQueueStatus();
      setState({
        total: status.total,
        byStatus: {
          pending: status.pending,
          failed: status.failed,
          retrying: status.syncing,
        },
        loading: false,
      });
    } catch {
      setState((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, POLL_INTERVAL);
    return () => clearInterval(timer);
  }, [refresh]);

  // Also listen for queue change events via BroadcastChannel
  useEffect(() => {
    let channel: BroadcastChannel | null = null;
    try {
      channel = new BroadcastChannel('pos-sync-channel');
      channel.onmessage = (event) => {
        const { type } = event.data ?? {};
        if (type === 'QUEUE_UPDATED' || type === 'SYNC_COMPLETED') {
          refresh();
        }
      };
    } catch {
      // BroadcastChannel not supported
    }
    return () => {
      channel?.close();
    };
  }, [refresh]);

  return { ...state, refresh };
}
