'use client';

import { cn } from '@/lib/utils';

interface CategoryChip {
  name: string;
  slug: string;
}

interface CategoryQuickFiltersProps {
  categories: CategoryChip[];
  activeCategory: string;
  onCategoryChange: (slug: string) => void;
  className?: string;
}

export function CategoryQuickFilters({
  categories,
  activeCategory,
  onCategoryChange,
  className,
}: CategoryQuickFiltersProps) {
  if (categories.length === 0) return null;

  const isAllActive = !activeCategory;

  return (
    <div
      className={cn(
        'flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600',
        className,
      )}
      role="group"
      aria-label="Filter by category"
    >
      <button
        type="button"
        onClick={() => onCategoryChange('')}
        className={cn(
          'inline-flex shrink-0 items-center rounded-full border px-3 py-1.5 text-sm font-medium transition-colors',
          isAllActive
            ? 'border-green-600 bg-green-600 text-white dark:border-green-500 dark:bg-green-500'
            : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
        )}
      >
        All
      </button>

      {categories.map((cat) => {
        const isActive = activeCategory === cat.slug;
        return (
          <button
            key={cat.slug}
            type="button"
            onClick={() => onCategoryChange(cat.slug)}
            className={cn(
              'inline-flex shrink-0 items-center rounded-full border px-3 py-1.5 text-sm font-medium transition-colors',
              isActive
                ? 'border-green-600 bg-green-600 text-white dark:border-green-500 dark:bg-green-500'
                : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700',
            )}
          >
            {cat.name}
          </button>
        );
      })}
    </div>
  );
}
