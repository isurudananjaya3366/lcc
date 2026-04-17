'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import type { StoreProduct, StoreProductImage } from '@/types/store/product';
import { StoreProductStatus } from '@/types/store/product';
import { ResultsHeader } from './ResultsHeader';
import { ResultsGrid } from './ResultsGrid';
import { ResultsPagination } from './ResultsPagination';
import { CategoryQuickFilters } from './CategoryQuickFilters';
import { DidYouMean } from './DidYouMean';
import {
  SearchFilterSidebar,
  SearchSort,
  SearchActiveFilters,
  SearchMobileFilterButton,
  SearchMobileFilterDrawer,
} from '@/components/storefront/search/SearchFilters';

// ─── Constants ──────────────────────────────────────────────────────────────

const STORE_API_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;
const PAGE_SIZE = 12;

// ─── API Types ──────────────────────────────────────────────────────────────

interface ApiProduct {
  id: string;
  slug: string;
  name: string;
  description: string;
  price: number;
  sale_price: number | null;
  currency: string;
  in_stock: boolean;
  sku: string;
  category: { id: string; slug: string; name: string };
  images: { id: string; url: string; alt_text: string; is_primary: boolean; order: number }[];
  rating: number;
  review_count: number;
}

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ApiProduct[];
}

// ─── Props ──────────────────────────────────────────────────────────────────

interface SearchResultsContainerProps {
  query: string;
  category: string;
  sort: string;
  page: string;
  minPrice: string;
  maxPrice: string;
  className?: string;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function mapApiProductToStoreProduct(p: ApiProduct): StoreProduct {
  const images: StoreProductImage[] = p.images.map((img) => ({
    id: img.id,
    url: img.url,
    altText: img.alt_text,
    isPrimary: img.is_primary,
    sortOrder: img.order,
  }));

  return {
    id: p.id,
    name: p.name,
    slug: p.slug,
    description: p.description,
    sku: p.sku,
    price: p.price,
    compareAtPrice: p.sale_price && p.sale_price < p.price ? p.price : undefined,
    currency: p.currency,
    status: p.in_stock ? StoreProductStatus.ACTIVE : StoreProductStatus.OUT_OF_STOCK,
    categoryId: p.category.id,
    categoryName: p.category.name,
    categorySlug: p.category.slug,
    images,
    variants: [],
    attributes: [],
    stockQuantity: p.in_stock ? 1 : 0,
    allowBackorder: false,
    isFeatured: false,
    isOnSale: p.sale_price != null && p.sale_price < p.price,
    tags: [],
    rating: p.rating,
    reviewCount: p.review_count,
    createdAt: '',
    updatedAt: '',
  };
}

// ─── Component ──────────────────────────────────────────────────────────────

export function SearchResultsContainer({
  query,
  category,
  sort,
  page,
  minPrice,
  maxPrice,
  className,
}: SearchResultsContainerProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const [products, setProducts] = useState<StoreProduct[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [categories, setCategories] = useState<{ name: string; slug: string }[]>([]);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const currentPage = Math.max(1, parseInt(page, 10) || 1);
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  // Fetch products when params change
  useEffect(() => {
    if (!query) {
      setProducts([]);
      setTotalCount(0);
      setError(null);
      return;
    }

    const controller = new AbortController();

    async function fetchProducts() {
      setIsLoading(true);
      setError(null);

      try {
        const params = new URLSearchParams({
          search: query,
          page: String(currentPage),
          page_size: String(PAGE_SIZE),
        });

        if (category) params.set('category', category);
        if (sort) params.set('ordering', sort);
        if (minPrice) params.set('min_price', minPrice);
        if (maxPrice) params.set('max_price', maxPrice);

        const res = await fetch(`${STORE_API_URL}/products/?${params.toString()}`, {
          signal: controller.signal,
        });

        if (!res.ok) {
          throw new Error(`Search failed (${res.status})`);
        }

        const data: ApiResponse = await res.json();
        const mapped = data.results.map(mapApiProductToStoreProduct);

        setProducts(mapped);
        setTotalCount(data.count);

        // Extract unique categories from results for quick filters
        const catMap = new Map<string, { name: string; slug: string }>();
        data.results.forEach((p) => {
          if (p.category?.slug && !catMap.has(p.category.slug)) {
            catMap.set(p.category.slug, {
              name: p.category.name,
              slug: p.category.slug,
            });
          }
        });
        setCategories(Array.from(catMap.values()));
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') return;
        setError(err instanceof Error ? err.message : 'An error occurred while searching.');
        setProducts([]);
        setTotalCount(0);
      } finally {
        setIsLoading(false);
      }
    }

    fetchProducts();

    return () => controller.abort();
  }, [query, category, sort, currentPage, minPrice, maxPrice]);

  const handleCategoryChange = useCallback(
    (slug: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (slug) {
        params.set('category', slug);
      } else {
        params.delete('category');
      }
      params.delete('page');
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, searchParams, pathname],
  );

  const handleDidYouMeanSelect = useCallback(
    (suggestion: string) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set('q', suggestion);
      params.delete('page');
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, searchParams, pathname],
  );

  const handleSortChange = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value) {
        params.set('sort', value);
      } else {
        params.delete('sort');
      }
      params.delete('page');
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, searchParams, pathname],
  );

  const activeFilters: Record<string, string> = {};
  if (category) activeFilters.category = category;
  if (minPrice) activeFilters.min_price = `LKR ${minPrice}`;
  if (maxPrice) activeFilters.max_price = `LKR ${maxPrice}`;
  if (sort) activeFilters.sort = sort;

  const activeFilterCount = Object.keys(activeFilters).length;

  const handleRemoveFilter = useCallback(
    (key: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (key === 'min_price' || key === 'max_price') {
        params.delete('min_price');
        params.delete('max_price');
      } else {
        params.delete(key);
      }
      params.delete('page');
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, searchParams, pathname],
  );

  const handleClearAllFilters = useCallback(() => {
    const params = new URLSearchParams();
    const q = searchParams.get('q');
    if (q) params.set('q', q);
    router.push(`${pathname}?${params.toString()}`);
  }, [router, searchParams, pathname]);

  // ─── Empty query state ────────────────────────────────────────────────────

  if (!query) {
    return (
      <section
        aria-label="Search results"
        className={cn('py-8 text-center', className)}
      >
        <p className="text-muted-foreground">
          Enter a search term to find products.
        </p>
      </section>
    );
  }

  // ─── Error state ──────────────────────────────────────────────────────────

  if (error && !isLoading) {
    return (
      <section
        aria-label="Search results"
        className={cn('space-y-4', className)}
      >
        <ResultsHeader query={query} totalCount={0} isLoading={false} />
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center dark:border-red-800 dark:bg-red-950">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-3 text-sm font-medium text-red-700 underline hover:text-red-800 dark:text-red-300 dark:hover:text-red-200"
          >
            Try again
          </button>
        </div>
      </section>
    );
  }

  // ─── Empty results state ──────────────────────────────────────────────────

  if (!isLoading && products.length === 0 && totalCount === 0) {
    return (
      <section
        aria-label="Search results"
        className={cn('space-y-4', className)}
      >
        <ResultsHeader query={query} totalCount={0} isLoading={false} />
        <DidYouMean suggestion={null} onSelect={handleDidYouMeanSelect} />
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mb-4 text-gray-300 dark:text-gray-600"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
            No products found
          </p>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Try adjusting your search or removing filters.
          </p>
        </div>
      </section>
    );
  }

  // ─── Results state ────────────────────────────────────────────────────────

  return (
    <section
      aria-label="Search results"
      className={cn('space-y-4', className)}
    >
      <ResultsHeader query={query} totalCount={totalCount} isLoading={isLoading} />

      {/* Toolbar: Active filters + Sort + Mobile filter button */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <SearchActiveFilters
          filters={activeFilters}
          onRemove={handleRemoveFilter}
          onClearAll={handleClearAllFilters}
        />
        <div className="flex items-center gap-2 ml-auto">
          <SearchSort currentSort={sort} onSortChange={handleSortChange} />
          <SearchMobileFilterButton
            onClick={() => setMobileFiltersOpen(true)}
            activeFilterCount={activeFilterCount}
          />
        </div>
      </div>

      <CategoryQuickFilters
        categories={categories}
        activeCategory={category}
        onCategoryChange={handleCategoryChange}
      />

      {/* Two-column layout: Sidebar + Results */}
      <div className="flex gap-6">
        <SearchFilterSidebar className="hidden w-60 shrink-0 lg:block" />

        <div className="min-w-0 flex-1 space-y-4">
          <ResultsGrid products={products} isLoading={isLoading} />

          <ResultsPagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalCount}
          />
        </div>
      </div>

      {/* Mobile filter drawer */}
      <SearchMobileFilterDrawer
        isOpen={mobileFiltersOpen}
        onClose={() => setMobileFiltersOpen(false)}
      >
        <SearchFilterSidebar />
      </SearchMobileFilterDrawer>
    </section>
  );
}
