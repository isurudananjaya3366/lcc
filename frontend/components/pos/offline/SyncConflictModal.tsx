// ================================================================
// SyncConflictModal — Task 77
// ================================================================

'use client';

import React, { useCallback, useState } from 'react';

type ResolutionAction = 'keepLocal' | 'useServer' | 'merge' | 'manual';

interface ConflictItem {
  id: string;
  entityType: string;
  entityName: string;
  localData: Record<string, unknown>;
  serverData: Record<string, unknown>;
  conflictingFields: string[];
  timestamp: Date;
}

interface SyncConflictModalProps {
  isOpen: boolean;
  conflicts: ConflictItem[];
  onResolve: (
    conflictId: string,
    action: ResolutionAction,
    mergedData?: Record<string, unknown>
  ) => void;
  onClose: () => void;
  className?: string;
}

export function SyncConflictModal({
  isOpen,
  conflicts,
  onResolve,
  onClose,
  className = '',
}: SyncConflictModalProps) {
  const [index, setIndex] = useState(0);
  const [action, setAction] = useState<ResolutionAction>('useServer');

  const conflict = conflicts[index];

  const handleApply = useCallback(() => {
    if (!conflict) return;
    onResolve(conflict.id, action);
    if (index < conflicts.length - 1) {
      setIndex((i) => i + 1);
      setAction('useServer');
    } else {
      onClose();
    }
  }, [conflict, action, index, conflicts.length, onResolve, onClose]);

  const handleApplyAll = useCallback(() => {
    for (const c of conflicts) onResolve(c.id, action);
    onClose();
  }, [conflicts, action, onResolve, onClose]);

  if (!isOpen || !conflict) return null;

  return (
    <div
      className={`fixed inset-0 bg-black/50 flex items-center justify-center z-50 ${className}`}
      role="dialog"
      aria-labelledby="conflict-modal-title"
      aria-modal="true"
    >
      <div
        className="bg-white dark:bg-gray-900 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6"
        onKeyDown={(e) => {
          if (e.key === 'Escape') onClose();
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2
            id="conflict-modal-title"
            className="text-lg font-semibold dark:text-white"
          >
            Resolve Sync Conflicts
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({index + 1} of {conflicts.length})
            </span>
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close conflicts dialog"
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            ✕
          </button>
        </div>

        {/* Entity info */}
        <div className="mb-4 text-sm text-gray-600 dark:text-gray-300">
          <span className="font-medium">{conflict.entityType}</span> —{' '}
          {conflict.entityName}
          <span className="ml-2 text-xs text-gray-400">
            {conflict.timestamp.toLocaleString()}
          </span>
        </div>

        {/* Side-by-side comparison */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Local */}
          <div>
            <div className="font-semibold text-sm px-3 py-2 bg-blue-50 dark:bg-blue-900/30 rounded-t border border-blue-200 dark:border-blue-700">
              Your Version (Local)
            </div>
            <div className="space-y-2 p-4 border border-t-0 border-blue-200 dark:border-blue-700 rounded-b">
              {conflict.conflictingFields.map((field) => (
                <div
                  key={field}
                  className="border-l-4 border-red-500 pl-3 py-1"
                >
                  <div className="text-xs font-medium text-gray-500">
                    {field}
                  </div>
                  <div className="text-sm bg-yellow-100 dark:bg-yellow-900/30 px-1 rounded inline-block">
                    {String(conflict.localData[field] ?? '—')}
                  </div>
                </div>
              ))}
            </div>
          </div>
          {/* Server */}
          <div>
            <div className="font-semibold text-sm px-3 py-2 bg-green-50 dark:bg-green-900/30 rounded-t border border-green-200 dark:border-green-700">
              Server Version
            </div>
            <div className="space-y-2 p-4 border border-t-0 border-green-200 dark:border-green-700 rounded-b">
              {conflict.conflictingFields.map((field) => (
                <div
                  key={field}
                  className="border-l-4 border-red-500 pl-3 py-1"
                >
                  <div className="text-xs font-medium text-gray-500">
                    {field}
                  </div>
                  <div className="text-sm bg-yellow-100 dark:bg-yellow-900/30 px-1 rounded inline-block">
                    {String(conflict.serverData[field] ?? '—')}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Resolution options */}
        <fieldset className="mb-6">
          <legend className="text-sm font-medium mb-2 dark:text-gray-200">
            Resolution
          </legend>
          <div className="space-y-2">
            {(
              [
                ['keepLocal', 'Keep local version'],
                ['useServer', 'Use server version'],
                ['merge', 'Auto-merge changes'],
                ['manual', 'Flag for manual review'],
              ] as [ResolutionAction, string][]
            ).map(([val, label]) => (
              <label
                key={val}
                className="flex items-center gap-2 text-sm cursor-pointer dark:text-gray-300"
              >
                <input
                  type="radio"
                  name="resolution"
                  value={val}
                  checked={action === val}
                  onChange={() => setAction(val)}
                  className="accent-blue-600"
                />
                {label}
              </label>
            ))}
          </div>
        </fieldset>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t dark:border-gray-700">
          <div className="flex gap-2">
            <button
              type="button"
              disabled={index === 0}
              onClick={() => setIndex((i) => i - 1)}
              className="px-3 py-2 text-sm border rounded disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
            >
              Previous
            </button>
            <button
              type="button"
              disabled={index === conflicts.length - 1}
              onClick={() => setIndex((i) => i + 1)}
              className="px-3 py-2 text-sm border rounded disabled:opacity-50 dark:border-gray-600 dark:text-gray-300"
            >
              Next
            </button>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleApplyAll}
              className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700"
            >
              Apply to All
            </button>
            <button
              type="button"
              onClick={handleApply}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Apply
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
