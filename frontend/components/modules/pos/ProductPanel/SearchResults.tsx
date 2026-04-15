'use client';

import { useRef, useEffect, useCallback, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { ProductImage } from './ProductImage';
import { PriceDisplay } from './PriceDisplay';
import { StockIndicator } from './StockIndicator';
import type { ProductSearchResult } from '../types';

interface SearchResultsProps {
  results: ProductSearchResult[];
  isLoading: boolean;
  error: string | null;
  onSelect: (product: ProductSearchResult) => void;
  onClose: () => void;
}

export function SearchResults({
  results,
  isLoading,
  error,
  onSelect,
  onClose,
}: SearchResultsProps) {
  const [activeIndex, setActiveIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [onClose]);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
        return;
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, Math.min(results.length, 10) - 1));
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, 0));
      }
      if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        const product = results[activeIndex];
        if (product) onSelect(product);
      }
    },
    [results, activeIndex, onSelect, onClose]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div
      ref={containerRef}
      className="absolute left-0 right-0 top-full z-50 mt-1 max-h-80 overflow-y-auto rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800"
      role="listbox"
    >
      {isLoading && (
        <div className="flex items-center justify-center gap-2 px-4 py-6 text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Searching...
        </div>
      )}

      {error && !isLoading && (
        <div className="px-4 py-6 text-center text-sm text-red-500">{error}</div>
      )}

      {!isLoading && !error && results.length === 0 && (
        <div className="px-4 py-6 text-center text-sm text-gray-500">No products found</div>
      )}

      {!isLoading &&
        !error &&
        results.slice(0, 10).map((product, index) => (
          <button
            key={product.id}
            onClick={() => onSelect(product)}
            className={`flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors hover:bg-gray-50 dark:hover:bg-gray-700 ${
              index === activeIndex ? 'bg-gray-50 dark:bg-gray-700' : ''
            }`}
            role="option"
            aria-selected={index === activeIndex}
          >
            <ProductImage src={product.imageUrl} alt={product.name} size="sm" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
                {product.name}
              </p>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span>{product.sku}</span>
                <StockIndicator quantity={product.stockQuantity} variant="dot" />
              </div>
            </div>
            <PriceDisplay price={product.price} size="sm" />
          </button>
        ))}

      {!isLoading && !error && results.length > 0 && (
        <div className="border-t border-gray-100 px-4 py-1.5 text-center text-xs text-gray-400 dark:border-gray-700">
          Showing {Math.min(results.length, 10)} of {results.length} results
        </div>
      )}
    </div>
  );
}
