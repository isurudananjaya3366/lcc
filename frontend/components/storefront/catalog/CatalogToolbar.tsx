'use client';

import { cn } from '@/lib/utils';
import type { StoreProductSort } from '@/types/store/product';
import { SortDropdown } from './SortDropdown';
import { ViewToggle } from './ViewToggle';
import { ActiveFilters } from './ActiveFilters';
import type { ActiveFilter } from './FilterTag';

interface CatalogToolbarProps {
  totalProducts?: number;
  sort: StoreProductSort;
  onSortChange: (sort: StoreProductSort) => void;
  view: 'grid' | 'list';
  onViewChange: (view: 'grid' | 'list') => void;
  activeFilters?: ActiveFilter[];
  onRemoveFilter?: (filterId: string) => void;
  onClearFilters?: () => void;
  isLoading?: boolean;
  className?: string;
}

export function CatalogToolbar({
  totalProducts,
  sort,
  onSortChange,
  view,
  onViewChange,
  activeFilters = [],
  onRemoveFilter,
  onClearFilters,
  isLoading,
  className,
}: CatalogToolbarProps) {
  return (
    <div className={cn('mb-4 rounded-lg border border-gray-200 bg-white px-4 py-3', className)}>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        {/* Left: product count */}
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium text-gray-900">
            {isLoading ? (
              <span className="text-gray-400">Loading…</span>
            ) : totalProducts != null ? (
              totalProducts > 0 ? (
                `${totalProducts.toLocaleString()} Product${totalProducts !== 1 ? 's' : ''}`
              ) : (
                <span className="text-gray-500">No products found</span>
              )
            ) : null}
          </p>
        </div>

        {/* Right: controls */}
        <div className="flex items-center gap-3">
          <SortDropdown value={sort} onChange={onSortChange} />
          <ViewToggle view={view} onChange={onViewChange} />
        </div>
      </div>

      {/* Active filters */}
      {activeFilters.length > 0 && onRemoveFilter && (
        <div className="mt-3 border-t border-gray-100 pt-3">
          <ActiveFilters
            filters={activeFilters}
            onRemove={onRemoveFilter}
            onClearAll={onClearFilters}
          />
        </div>
      )}
    </div>
  );
}
