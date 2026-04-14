'use client';

import { cn } from '@/lib/utils';

interface StockFilterProps {
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

const stockOptions = [
  { value: 'all', label: 'All Stock' },
  { value: 'low', label: 'Low Stock' },
  { value: 'out', label: 'Out of Stock' },
] as const;

export function StockFilter({ value, onChange, className }: StockFilterProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={cn(
        'min-w-[160px] rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100',
        className
      )}
      aria-label="Filter by stock level"
    >
      {stockOptions.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
