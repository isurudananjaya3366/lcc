// ================================================================
// CacheRefreshButton — Task 84
// ================================================================

'use client';

import React, { useState } from 'react';
import { useCacheRefresh } from '@/hooks/useCacheRefresh';

type EntityType =
  | 'all'
  | 'products'
  | 'customers'
  | 'sales'
  | 'inventory'
  | 'settings';

interface CacheRefreshButtonProps {
  className?: string;
}

const ENTITY_OPTIONS: { key: EntityType; label: string }[] = [
  { key: 'all', label: 'All Data' },
  { key: 'products', label: 'Products' },
  { key: 'customers', label: 'Customers' },
  { key: 'sales', label: 'Sales' },
  { key: 'inventory', label: 'Inventory' },
  { key: 'settings', label: 'Settings' },
];

export function CacheRefreshButton({
  className = '',
}: CacheRefreshButtonProps) {
  const { trigger, loading, progress, currentEntity, error, lastRefresh } =
    useCacheRefresh();
  const [selectedEntity, setSelectedEntity] = useState<EntityType>('all');
  const [open, setOpen] = useState(false);

  const handleRefresh = () => {
    setOpen(false);
    trigger(selectedEntity);
  };

  return (
    <div className={`relative inline-block ${className}`}>
      <div className="flex items-center gap-1">
        <button
          type="button"
          disabled={loading}
          onClick={handleRefresh}
          className="px-4 py-2 bg-green-600 text-white rounded-l-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium flex items-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin">⟳</span>
              Refreshing {currentEntity}… {progress}%
            </>
          ) : (
            <>
              <span>↻</span>
              Refresh Cache
            </>
          )}
        </button>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="px-2 py-2 bg-green-600 text-white rounded-r-lg border-l border-green-500 hover:bg-green-700 disabled:opacity-50"
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-label="Select entity to refresh"
        >
          ▾
        </button>
      </div>

      {/* Entity picker dropdown */}
      {open && (
        <div
          className="absolute right-0 mt-1 w-48 bg-white dark:bg-gray-900 border dark:border-gray-700 rounded-lg shadow-lg z-50"
          role="listbox"
        >
          {ENTITY_OPTIONS.map((opt) => (
            <button
              key={opt.key}
              type="button"
              role="option"
              aria-selected={selectedEntity === opt.key}
              onClick={() => {
                setSelectedEntity(opt.key);
                setOpen(false);
              }}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-800 ${
                selectedEntity === opt.key
                  ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 font-medium'
                  : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      )}

      {/* Status line */}
      {error && <p className="text-xs text-red-600 mt-1">{error}</p>}
      {lastRefresh && !loading && (
        <p className="text-xs text-gray-400 mt-1">
          Last: {lastRefresh.toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
