'use client';

import React, { type FC } from 'react';
import ProductSuggestionItem from './ProductSuggestionItem';
import type { SearchProduct } from '@/services/storefront/searchService';

export interface ProductSuggestionsProps {
  products: SearchProduct[];
  query: string;
  activeIndex: number;
  baseIndex: number;
  onSelect: (slug: string) => void;
}

const ProductSuggestions: FC<ProductSuggestionsProps> = ({
  products,
  query,
  activeIndex,
  baseIndex,
  onSelect,
}) => {
  if (products.length === 0) return null;

  return (
    <div role="group" aria-label="Product suggestions">
      <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
        Products
      </p>
      {products.slice(0, 5).map((product, i) => (
        <ProductSuggestionItem
          key={product.id}
          product={product}
          query={query}
          isActive={activeIndex === baseIndex + i}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
};

export default ProductSuggestions;
