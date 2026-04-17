'use client';

import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { StoreProduct } from '@/types/store/product';
import { CardImage } from './CardImage';
import { CardPrice } from './CardPrice';
import { CardRating } from './CardRating';
import { CardBadge } from './CardBadge';
import { CardAddToCart } from './CardAddToCart';

interface ListViewProps {
  products: StoreProduct[];
  isLoading?: boolean;
  className?: string;
}

function ListItemSkeleton() {
  return (
    <div className="flex animate-pulse gap-4 rounded-lg border border-gray-200 bg-white p-4">
      <div className="h-40 w-40 flex-shrink-0 rounded-md bg-gray-200" />
      <div className="flex flex-1 flex-col justify-between py-1">
        <div className="space-y-2">
          <div className="h-4 w-3/4 rounded bg-gray-200" />
          <div className="h-3 w-1/2 rounded bg-gray-200" />
          <div className="h-3 w-full rounded bg-gray-200" />
          <div className="h-3 w-5/6 rounded bg-gray-200" />
        </div>
        <div className="flex items-center justify-between pt-2">
          <div className="h-5 w-24 rounded bg-gray-200" />
          <div className="h-9 w-28 rounded bg-gray-200" />
        </div>
      </div>
    </div>
  );
}

export function ListView({ products, isLoading, className }: ListViewProps) {
  if (isLoading) {
    return (
      <div className={cn('space-y-4', className)}>
        {Array.from({ length: 4 }, (_, i) => (
          <ListItemSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div
        className={cn('flex flex-col items-center justify-center py-16 text-gray-500', className)}
      >
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
          className="mb-4 text-gray-300"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        <p className="text-lg font-medium">No products found</p>
        <p className="mt-1 text-sm text-gray-400">Try adjusting your filters or search terms.</p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      {products.map((product) => (
        <article
          key={product.id}
          className="group flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md sm:flex-row"
        >
          {/* Image */}
          <Link
            href={`/products/${product.slug}`}
            className="relative flex-shrink-0 sm:w-48 md:w-56"
          >
            <CardImage product={product} />
          </Link>

          {/* Content */}
          <div className="flex flex-1 flex-col justify-between p-4">
            <div>
              <div className="mb-1 flex flex-wrap items-center gap-2">
                <CardBadge product={product} />
              </div>
              <Link href={`/products/${product.slug}`}>
                <h3 className="text-base font-semibold text-gray-900 hover:text-blue-700 transition-colors line-clamp-1">
                  {product.name}
                </h3>
              </Link>
              {product.shortDescription && (
                <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                  {product.shortDescription}
                </p>
              )}
              <div className="mt-2">
                <CardRating product={product} />
              </div>
            </div>

            {/* Price + Cart */}
            <div className="mt-3 flex items-end justify-between gap-4">
              <CardPrice product={product} />
              <CardAddToCart product={product} />
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
