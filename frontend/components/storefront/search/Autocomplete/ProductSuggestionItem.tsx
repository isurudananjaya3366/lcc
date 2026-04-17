'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { formatCurrency } from '@/lib/store/config';
import HighlightMatch from './HighlightMatch';
import type { SearchProduct } from '@/services/storefront/searchService';

export interface ProductSuggestionItemProps {
  product: SearchProduct;
  query: string;
  isActive: boolean;
  onSelect: (slug: string) => void;
}

const ProductSuggestionItem: FC<ProductSuggestionItemProps> = ({
  product,
  query,
  isActive,
  onSelect,
}) => {
  const primaryImage = product.images?.find((img) => img.is_primary) ?? product.images?.[0];

  return (
    <button
      type="button"
      role="option"
      aria-selected={isActive}
      className={cn(
        'flex w-full items-center gap-3 px-3 py-2 text-left transition-colors',
        'hover:bg-gray-100 dark:hover:bg-gray-700',
        isActive && 'bg-gray-100 dark:bg-gray-700'
      )}
      onClick={() => onSelect(product.slug)}
      onMouseDown={(e) => e.preventDefault()}
    >
      {/* Thumbnail */}
      {primaryImage ? (
        <img
          src={primaryImage.url}
          alt={primaryImage.alt_text || product.name}
          className="h-10 w-10 rounded-md object-cover flex-shrink-0"
          loading="lazy"
        />
      ) : (
        <div className="flex h-10 w-10 items-center justify-center rounded-md bg-gray-100 dark:bg-gray-700 flex-shrink-0">
          <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
          </svg>
        </div>
      )}

      {/* Details */}
      <div className="flex-1 min-w-0">
        <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
          <HighlightMatch text={product.name} query={query} />
        </p>
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span className="font-medium text-green-700 dark:text-green-400">
            {formatCurrency(product.sale_price ?? product.price)}
          </span>
          {product.sale_price && product.sale_price < product.price && (
            <span className="line-through">{formatCurrency(product.price)}</span>
          )}
          {product.category && (
            <>
              <span aria-hidden="true">·</span>
              <span className="truncate">{product.category.name}</span>
            </>
          )}
        </div>
      </div>
    </button>
  );
};

export default ProductSuggestionItem;
