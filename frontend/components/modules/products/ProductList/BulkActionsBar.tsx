'use client';

import { Trash2, CheckCircle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BulkActionsBarProps {
  selectedCount: number;
  onBulkDelete?: () => void;
  onBulkActivate?: () => void;
  onBulkDeactivate?: () => void;
  onClearSelection: () => void;
  className?: string;
}

export function BulkActionsBar({
  selectedCount,
  onBulkDelete,
  onBulkActivate,
  onBulkDeactivate,
  onClearSelection,
  className,
}: BulkActionsBarProps) {
  if (selectedCount === 0) return null;

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 dark:border-blue-800 dark:bg-blue-900/20',
        className
      )}
    >
      <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
        {selectedCount} product{selectedCount > 1 ? 's' : ''} selected
      </span>
      <div className="flex items-center gap-1">
        {onBulkActivate && (
          <button
            type="button"
            onClick={onBulkActivate}
            className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-sm text-green-700 hover:bg-green-100 dark:text-green-400 dark:hover:bg-green-900/30"
          >
            <CheckCircle className="h-4 w-4" />
            Activate
          </button>
        )}
        {onBulkDeactivate && (
          <button
            type="button"
            onClick={onBulkDeactivate}
            className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          >
            <XCircle className="h-4 w-4" />
            Deactivate
          </button>
        )}
        {onBulkDelete && (
          <button
            type="button"
            onClick={onBulkDelete}
            className="inline-flex items-center gap-1 rounded-md px-3 py-1.5 text-sm text-red-700 hover:bg-red-100 dark:text-red-400 dark:hover:bg-red-900/30"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        )}
      </div>
      <button
        type="button"
        onClick={onClearSelection}
        className="ml-auto text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
      >
        Clear selection
      </button>
    </div>
  );
}
