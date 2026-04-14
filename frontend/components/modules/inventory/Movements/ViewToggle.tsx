'use client';

import { List, Table2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ViewToggleProps {
  view: 'timeline' | 'table';
  onViewChange: (view: 'timeline' | 'table') => void;
}

const views = [
  { key: 'timeline' as const, label: 'Timeline', icon: List },
  { key: 'table' as const, label: 'Table', icon: Table2 },
];

export function ViewToggle({ view, onViewChange }: ViewToggleProps) {
  return (
    <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1 dark:border-gray-700 dark:bg-gray-900">
      {views.map(({ key, label, icon: Icon }) => (
        <button
          key={key}
          type="button"
          onClick={() => onViewChange(key)}
          className={cn(
            'inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
            view === key
              ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
              : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
          )}
        >
          <Icon className="h-4 w-4" />
          {label}
        </button>
      ))}
    </div>
  );
}
