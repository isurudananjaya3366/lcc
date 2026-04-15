'use client';

import { Button } from '@/components/ui/button';
import { LayoutGrid, List } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ViewToggleProps {
  viewMode: 'cards' | 'table';
  onViewModeChange: (mode: 'cards' | 'table') => void;
}

export function ViewToggle({ viewMode, onViewModeChange }: ViewToggleProps) {
  return (
    <div className="flex border rounded-lg">
      <Button
        variant="ghost"
        size="sm"
        aria-label="Card view"
        className={cn('px-3 rounded-r-none', viewMode === 'cards' && 'bg-muted')}
        onClick={() => onViewModeChange('cards')}
      >
        <LayoutGrid className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        aria-label="Table view"
        className={cn('px-3 rounded-l-none', viewMode === 'table' && 'bg-muted')}
        onClick={() => onViewModeChange('table')}
      >
        <List className="h-4 w-4" />
      </Button>
    </div>
  );
}
