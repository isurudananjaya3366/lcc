'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

const SuggestionsLoading: FC = () => (
  <div className="p-3 space-y-3" role="status" aria-label="Loading suggestions">
    {Array.from({ length: 3 }).map((_, i) => (
      <div key={i} className="flex items-center gap-3 animate-pulse">
        <div
          className={cn(
            'h-10 w-10 rounded-md bg-gray-200 flex-shrink-0',
            'dark:bg-gray-700'
          )}
        />
        <div className="flex-1 space-y-2">
          <div className="h-3 w-3/4 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-2.5 w-1/2 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    ))}
    <span className="sr-only">Loading search suggestions…</span>
  </div>
);

export default SuggestionsLoading;
