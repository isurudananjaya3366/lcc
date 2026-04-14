'use client';

import { Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useWarehouses } from '@/hooks/queries/useWarehouses';

export interface StockFilterState {
  search: string;
  warehouse: string;
  stockLevel: string;
}

interface StockFiltersProps {
  filters: StockFilterState;
  onFilterChange: (key: keyof StockFilterState, value: string) => void;
  onClearFilters: () => void;
  className?: string;
}

const stockLevelOptions = [
  { label: 'All Levels', value: 'all' },
  { label: 'Low Stock', value: 'low' },
  { label: 'Out of Stock', value: 'out' },
  { label: 'Overstocked', value: 'over' },
  { label: 'In Stock', value: 'in' },
];

function countActiveFilters(filters: StockFilterState): number {
  let count = 0;
  if (filters.search.length > 0) count++;
  if (filters.warehouse !== 'all') count++;
  if (filters.stockLevel !== 'all') count++;
  return count;
}

export function StockFilters({
  filters,
  onFilterChange,
  onClearFilters,
  className,
}: StockFiltersProps) {
  const { data: warehousesData } = useWarehouses({ status: 'active' });
  const warehouses = warehousesData?.data ?? [];

  const activeCount = countActiveFilters(filters);

  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900',
        className
      )}
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        {/* Search */}
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name or SKU..."
            value={filters.search}
            onChange={(e) => onFilterChange('search', e.target.value)}
            className="w-full rounded-md border border-gray-300 bg-white py-2 pl-10 pr-8 text-sm placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
          />
          {filters.search && (
            <button
              type="button"
              onClick={() => onFilterChange('search', '')}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Warehouse Filter */}
        <select
          value={filters.warehouse}
          onChange={(e) => onFilterChange('warehouse', e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        >
          <option value="all">All Warehouses</option>
          {warehouses.map((wh) => (
            <option key={wh.id} value={wh.id}>
              {wh.name}
            </option>
          ))}
        </select>

        {/* Stock Level Filter */}
        <select
          value={filters.stockLevel}
          onChange={(e) => onFilterChange('stockLevel', e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        >
          {stockLevelOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Clear Filters */}
        {activeCount > 0 && (
          <button
            type="button"
            onClick={onClearFilters}
            className="inline-flex items-center gap-1 whitespace-nowrap text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
            aria-label={`Clear ${activeCount} filter${activeCount > 1 ? 's' : ''}`}
          >
            <X className="h-4 w-4" />
            Clear {activeCount > 1 ? `${activeCount} Filters` : 'Filter'}
          </button>
        )}
      </div>
    </div>
  );
}
