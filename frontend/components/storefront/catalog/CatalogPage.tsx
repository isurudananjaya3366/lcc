'use client';

import { useMemo, useState, useCallback } from 'react';
import { useProducts } from '@/hooks/queries/useStoreProducts';
import type { StoreProductFilters } from '@/lib/storeQueryKeys';
import type { StoreProductSort } from '@/types/store/product';
import { CatalogHeader } from './CatalogHeader';
import { CatalogContent } from './CatalogContent';
import { CatalogToolbar } from './CatalogToolbar';
import { SidebarContainer } from './SidebarContainer';
import { ProductGrid } from './ProductGrid';
import { ListView } from './ListView';
import { Pagination } from './Pagination';
import { FilterSidebar, EMPTY_FILTER_STATE } from './FilterSidebar';
import { MobileFilterDrawer } from './MobileFilterDrawer';
import type { FilterState } from './FilterSidebar';
import type { ActiveFilter } from './FilterTag';
import type { BreadcrumbItem } from './Breadcrumb';

const DEFAULT_PAGE_SIZE = 24;

interface CatalogPageProps {
  title: string;
  breadcrumbs: BreadcrumbItem[];
  categorySlug?: string;
  collectionSlug?: string;
  searchParams?: Record<string, string | string[]>;
}

function toStr(v: string | string[] | undefined): string | undefined {
  if (Array.isArray(v)) return v[0];
  return v;
}

function toNum(v: string | string[] | undefined): number | undefined {
  const s = toStr(v);
  if (!s) return undefined;
  const n = Number(s);
  return Number.isNaN(n) ? undefined : n;
}

function toArr(v: string | string[] | undefined): string[] {
  if (!v) return [];
  if (Array.isArray(v)) return v;
  return v.split(',').filter(Boolean);
}

function parseInitialFilters(sp: Record<string, string | string[]>): FilterState {
  const priceMin = toNum(sp.price_min);
  const priceMax = toNum(sp.price_max);
  return {
    categories: toArr(sp.category),
    priceRange:
      priceMin != null || priceMax != null ? { min: priceMin ?? 0, max: priceMax ?? 50000 } : null,
    attributes: {},
    colors: toArr(sp.color),
    sizes: toArr(sp.size),
    brands: toArr(sp.brand),
    inStock: toStr(sp.in_stock) === 'true',
    onSale: toStr(sp.on_sale) === 'true',
  };
}

function countActiveFilters(f: FilterState): number {
  let n = 0;
  n += f.categories.length;
  if (f.priceRange) n += 1;
  n += Object.values(f.attributes).reduce((s, a) => s + a.length, 0);
  n += f.colors.length;
  n += f.sizes.length;
  n += f.brands.length;
  if (f.inStock) n += 1;
  if (f.onSale) n += 1;
  return n;
}

export function CatalogPage({
  title,
  breadcrumbs,
  categorySlug,
  collectionSlug,
  searchParams,
}: CatalogPageProps) {
  const sp = searchParams ?? {};

  const [filterState, setFilterState] = useState<FilterState>(() => parseInitialFilters(sp));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [sort, setSort] = useState<StoreProductSort>(
    () => (toStr(sp.sort) as StoreProductSort) || 'newest'
  );
  const [view, setView] = useState<'grid' | 'list'>(() =>
    toStr(sp.view) === 'list' ? 'list' : 'grid'
  );
  const [currentPage, setCurrentPage] = useState(() => toNum(sp.page) ?? 1);

  const filters = useMemo<StoreProductFilters>(() => {
    return {
      category:
        categorySlug ??
        collectionSlug ??
        (filterState.categories.length ? filterState.categories.join(',') : toStr(sp.category)),
      search: toStr(sp.search),
      priceMin: filterState.priceRange?.min ?? toNum(sp.minPrice),
      priceMax: filterState.priceRange?.max ?? toNum(sp.maxPrice),
      sort: sort as StoreProductFilters['sort'],
      page: currentPage,
      limit: DEFAULT_PAGE_SIZE,
      inStock: filterState.inStock || toStr(sp.inStock) === 'true' || undefined,
      onSale: filterState.onSale || toStr(sp.onSale) === 'true' || undefined,
      featured: toStr(sp.featured) === 'true' ? true : undefined,
    };
  }, [categorySlug, collectionSlug, sp, filterState, sort, currentPage]);

  const { data, isLoading } = useProducts(filters);

  const products = data?.results ?? [];
  const totalCount = data?.count;
  const totalPages = totalCount ? Math.ceil(totalCount / DEFAULT_PAGE_SIZE) : 0;

  const handleFilterChange = useCallback((next: FilterState) => {
    setFilterState(next);
    setCurrentPage(1);
  }, []);

  const handleSortChange = useCallback((s: StoreProductSort) => {
    setSort(s);
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const activeCount = countActiveFilters(filterState);

  // Derive flat active filter list for toolbar display
  const activeFilters = useMemo<ActiveFilter[]>(() => {
    const list: ActiveFilter[] = [];
    filterState.categories.forEach((c) =>
      list.push({ id: `cat-${c}`, type: 'category', label: 'Category', value: c })
    );
    if (filterState.priceRange) {
      list.push({
        id: 'price',
        type: 'price',
        label: 'Price',
        value: `₨${filterState.priceRange.min.toLocaleString()} – ₨${filterState.priceRange.max.toLocaleString()}`,
      });
    }
    filterState.colors.forEach((c) =>
      list.push({ id: `color-${c}`, type: 'color', label: 'Color', value: c })
    );
    filterState.sizes.forEach((s) =>
      list.push({ id: `size-${s}`, type: 'size', label: 'Size', value: s })
    );
    filterState.brands.forEach((b) =>
      list.push({ id: `brand-${b}`, type: 'brand', label: 'Brand', value: b })
    );
    if (filterState.inStock)
      list.push({ id: 'inStock', type: 'availability', label: 'Availability', value: 'In Stock' });
    if (filterState.onSale)
      list.push({ id: 'onSale', type: 'availability', label: 'Sale', value: 'On Sale' });
    return list;
  }, [filterState]);

  const handleRemoveFilter = useCallback((filterId: string) => {
    setFilterState((prev) => {
      const next = { ...prev };
      if (filterId.startsWith('cat-'))
        next.categories = prev.categories.filter((c) => c !== filterId.slice(4));
      else if (filterId === 'price') next.priceRange = null;
      else if (filterId.startsWith('color-'))
        next.colors = prev.colors.filter((c) => c !== filterId.slice(6));
      else if (filterId.startsWith('size-'))
        next.sizes = prev.sizes.filter((s) => s !== filterId.slice(5));
      else if (filterId.startsWith('brand-'))
        next.brands = prev.brands.filter((b) => b !== filterId.slice(6));
      else if (filterId === 'inStock') next.inStock = false;
      else if (filterId === 'onSale') next.onSale = false;
      return next;
    });
    setCurrentPage(1);
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilterState(EMPTY_FILTER_STATE);
    setCurrentPage(1);
  }, []);

  const sidebarContent = (
    <FilterSidebar onFilterChange={handleFilterChange} initialFilters={filterState} />
  );

  return (
    <div className="py-8">
      <CatalogHeader
        breadcrumbs={breadcrumbs}
        title={title}
        productCount={totalCount}
        isLoading={isLoading}
      />

      {/* Mobile filter button */}
      <div className="mb-4 lg:hidden">
        <button
          type="button"
          onClick={() => setMobileOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
        >
          {/* Filter icon */}
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M2.628 1.601C5.028 1.206 7.49 1 10 1s4.973.206 7.372.601a.75.75 0 0 1 .628.74v2.288a2.25 2.25 0 0 1-.659 1.59l-4.682 4.683a2.25 2.25 0 0 0-.659 1.59v3.037c0 .684-.31 1.33-.844 1.757l-1.937 1.55A.75.75 0 0 1 8 18.25v-5.757a2.25 2.25 0 0 0-.659-1.591L2.659 6.22A2.25 2.25 0 0 1 2 4.629V2.34a.75.75 0 0 1 .628-.74Z"
              clipRule="evenodd"
            />
          </svg>
          Filters
          {activeCount > 0 && (
            <span className="inline-flex items-center justify-center rounded-full bg-blue-100 px-2 text-xs font-medium text-blue-700 min-w-[20px] h-5">
              {activeCount}
            </span>
          )}
        </button>
      </div>

      {/* Mobile drawer */}
      <MobileFilterDrawer
        isOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        activeFilterCount={activeCount}
      >
        <FilterSidebar onFilterChange={handleFilterChange} initialFilters={filterState} />
      </MobileFilterDrawer>

      {/* Toolbar: sort, view toggle, active filters */}
      <CatalogToolbar
        totalProducts={totalCount}
        sort={sort}
        onSortChange={handleSortChange}
        view={view}
        onViewChange={setView}
        activeFilters={activeFilters}
        onRemoveFilter={handleRemoveFilter}
        onClearFilters={handleClearFilters}
        isLoading={isLoading}
      />

      <CatalogContent sidebar={<SidebarContainer>{sidebarContent}</SidebarContainer>}>
        {view === 'grid' ? (
          <ProductGrid products={products} isLoading={isLoading} />
        ) : (
          <ListView products={products} isLoading={isLoading} />
        )}

        {totalPages > 1 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
            pageSize={DEFAULT_PAGE_SIZE}
            totalItems={totalCount}
            isLoading={isLoading}
          />
        )}
      </CatalogContent>
    </div>
  );
}
