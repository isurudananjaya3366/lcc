'use client';

import * as React from 'react';
import { type Table } from '@tanstack/react-table';
import { Search, X, SlidersHorizontal } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface TableToolbarProps<TData> {
  table: Table<TData>;
  globalFilter?: string;
  onGlobalFilterChange?: (value: string) => void;
  filterComponent?: React.ReactNode;
  actionComponent?: React.ReactNode;
  className?: string;
}

function TableToolbar<TData>({
  table,
  globalFilter = '',
  onGlobalFilterChange,
  filterComponent,
  actionComponent,
  className,
}: TableToolbarProps<TData>) {
  const activeFilters = table.getState().columnFilters;
  const selectedCount = table.getFilteredSelectedRowModel().rows.length;

  const clearAllFilters = () => {
    table.resetColumnFilters();
    onGlobalFilterChange?.('');
  };

  return (
    <div className={cn('flex flex-col gap-2 py-4', className)}>
      <div className="flex items-center gap-2">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search..."
            value={globalFilter}
            onChange={(e) => onGlobalFilterChange?.(e.target.value)}
            className="pl-8"
          />
          {globalFilter && (
            <button
              type="button"
              onClick={() => onGlobalFilterChange?.('')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Custom Filters */}
        {filterComponent}

        <div className="ml-auto flex items-center gap-2">
          {/* Selection Info */}
          {selectedCount > 0 && (
            <span className="text-sm text-muted-foreground">
              {selectedCount} selected
            </span>
          )}

          {/* Custom Actions */}
          {actionComponent}
        </div>
      </div>

      {/* Active Filter Chips */}
      {activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-1">
          {activeFilters.map((filter) => (
            <Badge key={filter.id} variant="secondary" className="gap-1">
              {filter.id}: {String(filter.value)}
              <button
                type="button"
                onClick={() =>
                  table.getColumn(filter.id)?.setFilterValue(undefined)
                }
                className="ml-0.5 rounded-full hover:bg-muted-foreground/20"
                aria-label={`Remove ${filter.id} filter`}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="h-6 px-2 text-xs"
          >
            Clear all
          </Button>
        </div>
      )}
    </div>
  );
}

export { TableToolbar };
