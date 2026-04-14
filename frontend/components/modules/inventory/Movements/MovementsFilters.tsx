'use client';

import { Search, X } from 'lucide-react';
import { useWarehouses } from '@/hooks/queries/useWarehouses';
import type { MovementFilters } from '@/hooks/queries/useStockMovements';

interface MovementsFiltersProps {
  filters: MovementFilters;
  onFilterChange: (filters: MovementFilters) => void;
}

const movementTypeOptions = [
  { label: 'All Types', value: 'all' },
  { label: 'Stock In', value: 'in' },
  { label: 'Stock Out', value: 'out' },
  { label: 'Adjustment', value: 'adjustment' },
  { label: 'Transfer', value: 'transfer' },
];

const datePresets = [
  { label: 'Today', days: 0 },
  { label: 'Last 7 days', days: 7 },
  { label: 'Last 30 days', days: 30 },
  { label: 'This month', days: -1 },
];

function getDateRange(days: number): { startDate: string; endDate: string } {
  const end = new Date();
  const start = new Date();
  if (days === -1) {
    start.setDate(1);
  } else if (days === 0) {
    start.setHours(0, 0, 0, 0);
  } else {
    start.setDate(start.getDate() - days);
  }
  return {
    startDate: start.toISOString().split('T')[0],
    endDate: end.toISOString().split('T')[0],
  };
}

export function MovementsFilters({ filters, onFilterChange }: MovementsFiltersProps) {
  const { data: warehousesData } = useWarehouses({ status: 'active' });
  const warehouses = warehousesData?.data ?? [];

  const hasActiveFilters =
    filters.productId ||
    filters.warehouseId ||
    (filters.movementType && filters.movementType !== 'all') ||
    filters.startDate ||
    filters.endDate;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        {/* Date Presets */}
        <div className="flex gap-1">
          {datePresets.map((preset) => {
            const range = getDateRange(preset.days);
            const isActive =
              filters.startDate === range.startDate && filters.endDate === range.endDate;
            return (
              <button
                key={preset.label}
                type="button"
                onClick={() => onFilterChange({ ...filters, ...range })}
                className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                }`}
              >
                {preset.label}
              </button>
            );
          })}
        </div>

        {/* Movement Type */}
        <select
          value={filters.movementType ?? 'all'}
          onChange={(e) =>
            onFilterChange({
              ...filters,
              movementType: e.target.value as MovementFilters['movementType'],
            })
          }
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        >
          {movementTypeOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Product Search */}
        <div className="relative flex-1 sm:max-w-xs">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Filter by product..."
            value={filters.productId ?? ''}
            onChange={(e) =>
              onFilterChange({
                ...filters,
                productId: e.target.value || undefined,
              })
            }
            className="w-full rounded-md border border-gray-300 bg-white py-2 pl-10 pr-3 text-sm placeholder:text-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
          />
        </div>

        {/* Warehouse Filter */}
        <select
          value={filters.warehouseId ?? ''}
          onChange={(e) =>
            onFilterChange({
              ...filters,
              warehouseId: e.target.value || undefined,
            })
          }
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
        >
          <option value="">All Warehouses</option>
          {warehouses.map((wh) => (
            <option key={wh.id} value={wh.id}>
              {wh.name}
            </option>
          ))}
        </select>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <button
            type="button"
            onClick={() =>
              onFilterChange({
                movementType: 'all',
                productId: undefined,
                warehouseId: undefined,
                startDate: undefined,
                endDate: undefined,
              })
            }
            className="inline-flex items-center gap-1 whitespace-nowrap text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <X className="h-4 w-4" />
            Clear Filters
          </button>
        )}
      </div>
    </div>
  );
}
