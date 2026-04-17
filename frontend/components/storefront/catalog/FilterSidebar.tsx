'use client';

import { useState, useCallback, useMemo } from 'react';
import { cn } from '@/lib/utils';
import type { StoreCategory } from '@/types/store/category';
import type { StoreProductAttribute } from '@/types/store/product';
import { FilterSection } from './FilterSection';
import { CategoryFilter } from './CategoryFilter';
import { PriceRangeFilter } from './PriceRangeFilter';
import { AttributeFilter } from './AttributeFilter';
import { ColorFilter } from './ColorFilter';
import { SizeFilter } from './SizeFilter';
import { BrandFilter } from './BrandFilter';
import { AvailabilityFilter } from './AvailabilityFilter';
import { ClearAllFilters } from './ClearAllFilters';

export interface FilterState {
  categories: string[];
  priceRange: { min: number; max: number } | null;
  attributes: Record<string, string[]>;
  colors: string[];
  sizes: string[];
  brands: string[];
  inStock: boolean;
  onSale: boolean;
}

export const EMPTY_FILTER_STATE: FilterState = {
  categories: [],
  priceRange: null,
  attributes: {},
  colors: [],
  sizes: [],
  brands: [],
  inStock: false,
  onSale: false,
};

interface FilterSidebarProps {
  categories?: StoreCategory[];
  attributes?: StoreProductAttribute[];
  colors?: string[];
  sizes?: string[];
  brands?: string[];
  onFilterChange: (filters: FilterState) => void;
  initialFilters?: FilterState;
  className?: string;
}

export function FilterSidebar({
  categories = [],
  attributes = [],
  colors = [],
  sizes = [],
  brands = [],
  onFilterChange,
  initialFilters,
  className,
}: FilterSidebarProps) {
  const [filters, setFilters] = useState<FilterState>(() => initialFilters ?? EMPTY_FILTER_STATE);

  const update = useCallback(
    (partial: Partial<FilterState>) => {
      setFilters((prev) => {
        const next = { ...prev, ...partial };
        onFilterChange(next);
        return next;
      });
    },
    [onFilterChange]
  );

  const hasActiveFilters = useMemo(() => {
    return (
      filters.categories.length > 0 ||
      filters.priceRange !== null ||
      Object.keys(filters.attributes).length > 0 ||
      filters.colors.length > 0 ||
      filters.sizes.length > 0 ||
      filters.brands.length > 0 ||
      filters.inStock ||
      filters.onSale
    );
  }, [filters]);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    count += filters.categories.length;
    if (filters.priceRange) count += 1;
    count += Object.values(filters.attributes).reduce((sum, arr) => sum + arr.length, 0);
    count += filters.colors.length;
    count += filters.sizes.length;
    count += filters.brands.length;
    if (filters.inStock) count += 1;
    if (filters.onSale) count += 1;
    return count;
  }, [filters]);

  const clearAll = useCallback(() => {
    setFilters(EMPTY_FILTER_STATE);
    onFilterChange(EMPTY_FILTER_STATE);
  }, [onFilterChange]);

  return (
    <div className={cn('space-y-0', className)}>
      {/* Header */}
      <div className="flex items-center justify-between pb-2">
        <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
        <ClearAllFilters onClear={clearAll} hasActiveFilters={hasActiveFilters} />
      </div>

      {/* Category */}
      {categories.length > 0 && (
        <FilterSection title="Category" badge={filters.categories.length || undefined} defaultOpen>
          <CategoryFilter
            categories={categories}
            selected={filters.categories}
            onChange={(categories) => update({ categories })}
          />
        </FilterSection>
      )}

      {/* Price Range */}
      <FilterSection title="Price" badge={filters.priceRange ? 1 : undefined} defaultOpen>
        <PriceRangeFilter
          value={filters.priceRange}
          onChange={(priceRange) => update({ priceRange })}
          currency="₨"
        />
      </FilterSection>

      {/* Colors */}
      {colors.length > 0 && (
        <FilterSection title="Color" badge={filters.colors.length || undefined} defaultOpen>
          <ColorFilter
            colors={colors}
            selected={filters.colors}
            onChange={(colors) => update({ colors })}
          />
        </FilterSection>
      )}

      {/* Sizes */}
      {sizes.length > 0 && (
        <FilterSection title="Size" badge={filters.sizes.length || undefined} defaultOpen={false}>
          <SizeFilter
            sizes={sizes}
            selected={filters.sizes}
            onChange={(sizes) => update({ sizes })}
          />
        </FilterSection>
      )}

      {/* Brands */}
      {brands.length > 0 && (
        <FilterSection title="Brand" badge={filters.brands.length || undefined} defaultOpen={false}>
          <BrandFilter
            brands={brands}
            selected={filters.brands}
            onChange={(brands) => update({ brands })}
          />
        </FilterSection>
      )}

      {/* Attributes */}
      {attributes.length > 0 && (
        <FilterSection
          title="Attributes"
          badge={Object.values(filters.attributes).reduce((s, a) => s + a.length, 0) || undefined}
          defaultOpen={false}
        >
          <AttributeFilter
            attributes={attributes}
            selected={filters.attributes}
            onChange={(attributes) => update({ attributes })}
          />
        </FilterSection>
      )}

      {/* Availability */}
      <FilterSection title="Availability" defaultOpen={false}>
        <AvailabilityFilter
          inStock={filters.inStock}
          onSale={filters.onSale}
          onInStockChange={(inStock) => update({ inStock })}
          onOnSaleChange={(onSale) => update({ onSale })}
        />
      </FilterSection>
    </div>
  );
}
