'use client';

import { useCallback } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { SearchCategoryFilter } from './SearchCategoryFilter';
import { SearchPriceFilter } from './SearchPriceFilter';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SearchFilterSidebarProps {
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchFilterSidebar({ className }: SearchFilterSidebarProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const activeCategory = searchParams.get('category') ?? '';
  const minPrice = searchParams.get('min_price') ?? '';
  const maxPrice = searchParams.get('max_price') ?? '';

  const updateParams = useCallback(
    (updates: Record<string, string>) => {
      const params = new URLSearchParams(searchParams.toString());
      Object.entries(updates).forEach(([key, value]) => {
        if (value) {
          params.set(key, value);
        } else {
          params.delete(key);
        }
      });
      params.delete('page');
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, searchParams, pathname],
  );

  const handleCategoryChange = useCallback(
    (slug: string) => updateParams({ category: slug }),
    [updateParams],
  );

  const handlePriceChange = useCallback(
    (min: string, max: string) => updateParams({ min_price: min, max_price: max }),
    [updateParams],
  );

  return (
    <aside className={cn('space-y-6', className)}>
      <SearchCategoryFilter
        activeCategory={activeCategory}
        onCategoryChange={handleCategoryChange}
      />

      <div className="border-t border-gray-200 pt-4 dark:border-gray-700">
        <SearchPriceFilter
          minPrice={minPrice}
          maxPrice={maxPrice}
          onPriceChange={handlePriceChange}
        />
      </div>
    </aside>
  );
}
