'use client';

import { cn } from '@/lib/utils';

type ViewMode = 'grid' | 'list';

interface ViewToggleProps {
  view: ViewMode;
  onChange: (view: ViewMode) => void;
  className?: string;
}

export function ViewToggle({ view, onChange, className }: ViewToggleProps) {
  return (
    <div
      className={cn('hidden sm:inline-flex rounded-lg border border-gray-300 bg-white', className)}
      role="radiogroup"
      aria-label="View mode"
    >
      {/* Grid button */}
      <button
        type="button"
        onClick={() => onChange('grid')}
        className={cn(
          'inline-flex items-center justify-center rounded-l-lg p-2 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset',
          view === 'grid'
            ? 'bg-gray-900 text-white'
            : 'bg-white text-gray-500 hover:bg-gray-50 hover:text-gray-700'
        )}
        aria-label="Grid view"
        aria-pressed={view === 'grid'}
        role="radio"
        aria-checked={view === 'grid'}
      >
        <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path
            fillRule="evenodd"
            d="M4.25 2A2.25 2.25 0 0 0 2 4.25v2.5A2.25 2.25 0 0 0 4.25 9h2.5A2.25 2.25 0 0 0 9 6.75v-2.5A2.25 2.25 0 0 0 6.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 2 13.25v2.5A2.25 2.25 0 0 0 4.25 18h2.5A2.25 2.25 0 0 0 9 15.75v-2.5A2.25 2.25 0 0 0 6.75 11h-2.5Zm9-9A2.25 2.25 0 0 0 11 4.25v2.5A2.25 2.25 0 0 0 13.25 9h2.5A2.25 2.25 0 0 0 18 6.75v-2.5A2.25 2.25 0 0 0 15.75 2h-2.5Zm0 9A2.25 2.25 0 0 0 11 13.25v2.5A2.25 2.25 0 0 0 13.25 18h2.5A2.25 2.25 0 0 0 18 15.75v-2.5A2.25 2.25 0 0 0 15.75 11h-2.5Z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      {/* List button */}
      <button
        type="button"
        onClick={() => onChange('list')}
        className={cn(
          'inline-flex items-center justify-center rounded-r-lg border-l border-gray-300 p-2 text-sm transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset',
          view === 'list'
            ? 'bg-gray-900 text-white'
            : 'bg-white text-gray-500 hover:bg-gray-50 hover:text-gray-700'
        )}
        aria-label="List view"
        aria-pressed={view === 'list'}
        role="radio"
        aria-checked={view === 'list'}
      >
        <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path
            fillRule="evenodd"
            d="M2 3.75A.75.75 0 0 1 2.75 3h14.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 3.75Zm0 4.167a.75.75 0 0 1 .75-.75h14.5a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1-.75-.75Zm0 4.166a.75.75 0 0 1 .75-.75h14.5a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1-.75-.75Zm0 4.167a.75.75 0 0 1 .75-.75h14.5a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1-.75-.75Z"
            clipRule="evenodd"
          />
        </svg>
      </button>
    </div>
  );
}
