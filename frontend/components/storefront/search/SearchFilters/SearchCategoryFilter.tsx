'use client';

import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';

// ─── Types ──────────────────────────────────────────────────────────────────

interface Category {
  id: string;
  slug: string;
  name: string;
  product_count?: number;
}

interface SearchCategoryFilterProps {
  activeCategory: string;
  onCategoryChange: (slug: string) => void;
  className?: string;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const STORE_API_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchCategoryFilter({
  activeCategory,
  onCategoryChange,
  className,
}: SearchCategoryFilterProps) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchCategories() {
      setIsLoading(true);
      try {
        const res = await fetch(`${STORE_API_URL}/categories/`, {
          signal: controller.signal,
        });
        if (!res.ok) throw new Error('Failed to fetch categories');
        const data = await res.json();
        setCategories(Array.isArray(data) ? data : data.results ?? []);
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        setCategories([]);
      } finally {
        setIsLoading(false);
      }
    }

    fetchCategories();
    return () => controller.abort();
  }, []);

  if (isLoading) {
    return (
      <div className={cn('space-y-2', className)}>
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Category</h3>
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-5 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    );
  }

  if (categories.length === 0) return null;

  return (
    <div className={cn('space-y-2', className)}>
      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Category</h3>
      <ul className="space-y-1">
        {categories.map((cat) => {
          const isActive = activeCategory === cat.slug;
          return (
            <li key={cat.id}>
              <button
                type="button"
                onClick={() => onCategoryChange(isActive ? '' : cat.slug)}
                className={cn(
                  'flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors',
                  isActive
                    ? 'bg-primary/10 font-medium text-primary dark:bg-primary/20'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800',
                )}
              >
                <span
                  className={cn(
                    'flex h-4 w-4 shrink-0 items-center justify-center rounded border',
                    isActive
                      ? 'border-primary bg-primary text-white'
                      : 'border-gray-300 dark:border-gray-600',
                  )}
                >
                  {isActive && (
                    <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="2,6 5,9 10,3" />
                    </svg>
                  )}
                </span>
                <span className="flex-1 truncate">{cat.name}</span>
                {cat.product_count != null && (
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    ({cat.product_count})
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
