'use client';

import { cn } from '@/lib/utils';
import type { ProductCategory } from '@/types/product';

interface CategoryFilterProps {
  value: string;
  onChange: (value: string) => void;
  categories: ProductCategory[];
  isLoading?: boolean;
  className?: string;
}

export function CategoryFilter({
  value,
  onChange,
  categories,
  isLoading = false,
  className,
}: CategoryFilterProps) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={isLoading}
      className={cn(
        'min-w-[180px] rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100',
        isLoading && 'cursor-wait opacity-50',
        className
      )}
      aria-label="Filter by category"
    >
      <option value="">All Categories</option>
      {categories.map((category) => (
        <option key={category.id} value={category.id}>
          {category.parentId ? `↳ ${category.name}` : category.name}
        </option>
      ))}
    </select>
  );
}
