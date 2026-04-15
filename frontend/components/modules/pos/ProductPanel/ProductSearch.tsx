'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, X, Loader2, ScanBarcode } from 'lucide-react';
import { useDebounce } from '@/hooks/useDebounce';
import { posService } from '@/services/pos';
import { SearchResults } from './SearchResults';
import { useBarcodeScanner } from '../hooks/useBarcodeScanner';
import { usePOS } from '../context/POSContext';
import type { ProductSearchResult } from '../types';

interface ProductSearchProps {
  onSelect?: (product: ProductSearchResult) => void;
}

export function ProductSearch({ onSelect: onExternalSelect }: ProductSearchProps = {}) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ProductSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);
  const debouncedQuery = useDebounce(query, 300);
  const { addToCart, openModal } = usePOS();

  // Barcode scanner handler
  useBarcodeScanner(async (barcode) => {
    setQuery(barcode);
    setIsLoading(true);
    try {
      const product = await posService.scanBarcode(barcode);
      if (product.hasVariants) {
        setResults([product]);
        setIsOpen(true);
      } else {
        addToCart({
          productId: product.id,
          productName: product.name,
          sku: product.sku,
          unitPrice: product.price,
          originalPrice: product.price,
          quantity: 1,
          taxRate: 0,
          isTaxable: true,
          imageUrl: product.imageUrl,
        });
        setQuery('');
      }
    } catch {
      setError('Product not found');
      setIsOpen(true);
    } finally {
      setIsLoading(false);
    }
  });

  // Auto-focus on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Search on debounced query change
  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setIsLoading(true);
    setError(null);

    posService
      .searchProducts(debouncedQuery)
      .then((data) => {
        setResults(data);
        setIsOpen(true);
      })
      .catch((err) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        setError('Search failed. Please try again.');
        setIsOpen(true);
      })
      .finally(() => setIsLoading(false));

    return () => controller.abort();
  }, [debouncedQuery]);

  const handleSelect = useCallback(
    (product: ProductSearchResult) => {
      if (onExternalSelect) {
        onExternalSelect(product);
      } else if (product.hasVariants) {
        setResults([product]);
        openModal('variant_select');
      } else {
        addToCart({
          productId: product.id,
          productName: product.name,
          sku: product.sku,
          unitPrice: product.price,
          originalPrice: product.price,
          quantity: 1,
          taxRate: 0,
          isTaxable: true,
          imageUrl: product.imageUrl,
        });
      }
      setQuery('');
      setIsOpen(false);
      inputRef.current?.focus();
    },
    [addToCart, openModal, onExternalSelect]
  );

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
    inputRef.current?.focus();
  };

  return (
    <div className="relative">
      <div className="relative flex items-center">
        <Search className="absolute left-3 h-4 w-4 text-gray-400" />
        <span title="Supports barcode scanning">
          <ScanBarcode
            className="absolute left-8 h-3.5 w-3.5 text-gray-300"
            aria-hidden="true"
          />
        </span>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder="Search or scan barcode..."
          className="w-full rounded-md border border-gray-300 bg-white py-2.5 pl-14 pr-10 text-sm placeholder:text-gray-400 focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100"
          autoComplete="off"
          data-pos-search
          aria-label="Search products"
        />
        {isLoading && <Loader2 className="absolute right-8 h-4 w-4 animate-spin text-gray-400" />}
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 rounded-sm p-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {isOpen && (
        <SearchResults
          results={results}
          isLoading={isLoading}
          error={error}
          onSelect={handleSelect}
          onClose={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
