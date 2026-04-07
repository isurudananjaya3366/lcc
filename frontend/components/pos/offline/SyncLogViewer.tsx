// ================================================================
// SyncLogViewer — Task 80
// ================================================================

'use client';

import React, { useMemo, useState } from 'react';

// ----------------------------------------------------------------
// Types
// ----------------------------------------------------------------

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

interface SyncLogViewerProps {
  entries?: SyncLogEntry[];
  pageSize?: 10 | 25 | 50 | 100;
  showFilters?: boolean;
  className?: string;
}

// ----------------------------------------------------------------
// Component
// ----------------------------------------------------------------

const STATUS_ICON: Record<string, string> = {
  Success: '✅',
  Failed: '❌',
  Partial: '⚠️',
};
const STATUS_COLOR: Record<string, string> = {
  Success: 'text-green-600',
  Failed: 'text-red-600',
  Partial: 'text-yellow-600',
};

export function SyncLogViewer({
  entries = [],
  pageSize = 25,
  showFilters = true,
  className = '',
}: SyncLogViewerProps) {
  const [page, setPage] = useState(0);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return entries.filter((e) => {
      if (filterType !== 'all' && e.type !== filterType) return false;
      if (filterStatus !== 'all' && e.status !== filterStatus) return false;
      return true;
    });
  }, [entries, filterType, filterStatus]);

  const totalPages = Math.ceil(filtered.length / pageSize);
  const paged = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return (
    <div className={`${className}`}>
      {/* Filters */}
      {showFilters && (
        <div className="flex gap-3 mb-4 flex-wrap">
          <select
            value={filterType}
            onChange={(e) => {
              setFilterType(e.target.value);
              setPage(0);
            }}
            className="px-3 py-2 border rounded text-sm dark:bg-gray-800 dark:border-gray-600 dark:text-gray-200"
            aria-label="Filter by type"
          >
            <option value="all">All Types</option>
            {['Push', 'Pull', 'Full', 'Auto', 'Manual'].map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <select
            value={filterStatus}
            onChange={(e) => {
              setFilterStatus(e.target.value);
              setPage(0);
            }}
            className="px-3 py-2 border rounded text-sm dark:bg-gray-800 dark:border-gray-600 dark:text-gray-200"
            aria-label="Filter by status"
          >
            <option value="all">All Statuses</option>
            {['Success', 'Failed', 'Partial'].map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto border rounded-lg dark:border-gray-700">
        <table
          className="w-full text-sm"
          role="grid"
          aria-label="Sync history log"
        >
          <thead className="bg-gray-50 dark:bg-gray-800 sticky top-0">
            <tr>
              <th className="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">
                Timestamp
              </th>
              <th className="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">
                Type
              </th>
              <th className="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">
                Status
              </th>
              <th className="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">
                Entities
              </th>
              <th className="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">
                Duration
              </th>
              <th className="text-left px-4 py-2 font-medium text-gray-600 dark:text-gray-300">
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {paged.map((entry) => (
              <React.Fragment key={entry.id}>
                <tr className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-4 py-2 text-gray-700 dark:text-gray-300">
                    {entry.timestamp.toLocaleString()}
                  </td>
                  <td className="px-4 py-2">{entry.type}</td>
                  <td className={`px-4 py-2 ${STATUS_COLOR[entry.status]}`}>
                    {STATUS_ICON[entry.status]} {entry.status}
                  </td>
                  <td className="px-4 py-2 text-gray-500 dark:text-gray-400">
                    {Object.entries(entry.entities)
                      .map(([k, v]) => `${v} ${k}`)
                      .join(', ') || '—'}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">
                    {(entry.duration / 1000).toFixed(1)}s
                  </td>
                  <td className="px-4 py-2">
                    <button
                      type="button"
                      onClick={() =>
                        setExpandedId(expandedId === entry.id ? null : entry.id)
                      }
                      className="text-blue-600 dark:text-blue-400 text-xs hover:underline"
                      aria-expanded={expandedId === entry.id}
                    >
                      {expandedId === entry.id ? 'Hide' : 'Details'}
                    </button>
                  </td>
                </tr>
                {expandedId === entry.id && (
                  <tr>
                    <td
                      colSpan={6}
                      className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20 px-6 py-4"
                    >
                      <div className="space-y-2 text-xs">
                        <p>
                          <strong>Triggered by:</strong> {entry.triggeredBy}
                        </p>
                        {entry.errors.length > 0 && (
                          <div>
                            <strong>Errors:</strong>
                            <ul className="list-disc ml-4 mt-1">
                              {entry.errors.map((e, i) => (
                                <li key={i}>
                                  <span className="font-mono">{e.code}</span>:{' '}
                                  {e.message}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {entry.conflicts.length > 0 && (
                          <p>
                            <strong>Conflicts:</strong> {entry.conflicts.length}{' '}
                            (
                            {entry.conflicts
                              .map((c) => c.entityType)
                              .join(', ')}
                            )
                          </p>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
            {paged.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                  No sync history entries
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 pt-4 border-t dark:border-gray-700">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {filtered.length} entries
          </span>
          <div className="flex gap-1">
            <button
              type="button"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="px-2 py-1 border rounded text-sm disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
            >
              Prev
            </button>
            <span className="px-2 py-1 text-sm text-gray-600 dark:text-gray-400">
              {page + 1}/{totalPages}
            </span>
            <button
              type="button"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="px-2 py-1 border rounded text-sm disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
