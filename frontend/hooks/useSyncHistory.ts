// ================================================================
// useSyncHistory — Task 80
// ================================================================

'use client';

import { useCallback, useEffect, useState } from 'react';

interface SyncLogEntry {
  id: string;
  timestamp: Date;
  type: 'Push' | 'Pull' | 'Full' | 'Auto' | 'Manual';
  status: 'Success' | 'Failed' | 'Partial';
  duration: number;
  entities: Record<string, number>;
  errors: { code: string; message: string }[];
  conflicts: { entityId: string; entityType: string }[];
  triggeredBy: string;
}

interface SyncHistoryFilters {
  type: string;
  status: string;
  dateRange: { start: Date | null; end: Date | null };
  search: string;
}

interface SyncHistoryState {
  entries: SyncLogEntry[];
  loading: boolean;
  error: string | null;
  filters: SyncHistoryFilters;
}

const STORAGE_KEY = 'pos_sync_history';

function loadEntries(): SyncLogEntry[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Array<Record<string, unknown>>;
    return parsed.map((e) => ({
      ...(e as unknown as SyncLogEntry),
      timestamp: new Date(e.timestamp as string),
    }));
  } catch {
    return [];
  }
}

export function useSyncHistory() {
  const [state, setState] = useState<SyncHistoryState>({
    entries: [],
    loading: true,
    error: null,
    filters: {
      type: 'all',
      status: 'all',
      dateRange: { start: null, end: null },
      search: '',
    },
  });

  useEffect(() => {
    setState((s) => ({ ...s, entries: loadEntries(), loading: false }));
  }, []);

  const setFilters = useCallback((filters: Partial<SyncHistoryFilters>) => {
    setState((s) => ({ ...s, filters: { ...s.filters, ...filters } }));
  }, []);

  const retrySync = useCallback(async (entryId: string) => {
    // Placeholder — the sync engine handles actual retry logic
    console.log(`Retry sync requested for entry: ${entryId}`);
  }, []);

  const exportLogs = useCallback(
    (format: 'json' | 'csv') => {
      const data = state.entries;
      if (format === 'json') {
        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sync-log-${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
      } else {
        const headers = [
          'id',
          'timestamp',
          'type',
          'status',
          'duration',
          'triggeredBy',
        ];
        const rows = data.map((e) =>
          headers.map((h) => String(e[h as keyof SyncLogEntry])).join(',')
        );
        const csv = [headers.join(','), ...rows].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sync-log-${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      }
    },
    [state.entries]
  );

  const clearHistory = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setState((s) => ({ ...s, entries: [] }));
  }, []);

  return {
    entries: state.entries,
    loading: state.loading,
    error: state.error,
    filters: state.filters,
    setFilters,
    retrySync,
    exportLogs,
    clearHistory,
  };
}
