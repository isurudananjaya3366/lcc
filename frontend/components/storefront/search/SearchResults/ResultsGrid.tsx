'use client';

import { cn } from '@/lib/utils';
import type { StoreProduct } from '@/types/store/product';
import { ProductCard } from '@/components/storefront/catalog/ProductCard';
import { ProductCardSkeleton } from '@/components/storefront/catalog/ProductCardSkeleton';

interface ResultsGridProps {
  products: StoreProduct[];
  isLoading: boolean;
  className?: string;
}

const SKELETON_COUNT = 8;

export function ResultsGrid({ products, isLoading, className }: ResultsGridProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          'grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4',
          className,
        )}
        aria-label="Loading search results"
        role="status"
      >
        {Array.from({ length: SKELETON_COUNT }, (_, i) => (
          <ProductCardSkeleton key={i} />
        ))}
        <span className="sr-only">Loading search results...</span>
      </div>
    );
  }

  if (products.length === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        'grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4',
        className,
      )}
    >
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
