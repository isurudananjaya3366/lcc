'use client';

import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/cn';

interface CollapseToggleProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

export function CollapseToggle({ isCollapsed, onToggle }: CollapseToggleProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className={cn(
        'flex h-8 w-8 items-center justify-center rounded-md text-gray-400 transition-colors',
        'hover:bg-slate-700 hover:text-white',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
      )}
      aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      aria-expanded={!isCollapsed}
    >
      {isCollapsed ? (
        <ChevronRight className="h-4 w-4 transition-transform duration-200" />
      ) : (
        <ChevronLeft className="h-4 w-4 transition-transform duration-200" />
      )}
    </button>
  );
}
