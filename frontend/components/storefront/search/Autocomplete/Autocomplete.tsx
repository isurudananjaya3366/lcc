'use client';

import React, { useCallback, useEffect, useRef, useState, type FC, type RefObject } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useDebounce } from '@/hooks/useDebounce';
import { getSearchSuggestions } from '@/services/storefront/searchService';
import type { SearchProduct, SearchCategory } from '@/services/storefront/searchService';
import ProductSuggestions from './ProductSuggestions';
import CategorySuggestions from './CategorySuggestions';
import SuggestionsLoading from './SuggestionsLoading';

export interface AutocompleteProps {
  query: string;
  isOpen: boolean;
  onClose: () => void;
  onSelect: (value: string) => void;
  inputRef: RefObject<HTMLInputElement | null>;
}

const Autocomplete: FC<AutocompleteProps> = ({ query, isOpen, onClose, onSelect, inputRef }) => {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const [products, setProducts] = useState<SearchProduct[]>([]);
  const [categories, setCategories] = useState<SearchCategory[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const debouncedQuery = useDebounce(query, 300);
  const totalItems = products.slice(0, 5).length + categories.slice(0, 5).length;

  // ─── Fetch suggestions ─────────────────────────────────────────────
  useEffect(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) {
      setProducts([]);
      setCategories([]);
      return;
    }

    let cancelled = false;
    setIsLoading(true);

    getSearchSuggestions(debouncedQuery).then((data) => {
      if (cancelled) return;
      setProducts(data.products);
      setCategories(data.categories);
      setIsLoading(false);
      setActiveIndex(-1);
    });

    return () => { cancelled = true; };
  }, [debouncedQuery]);

  // ─── Click outside to close ────────────────────────────────────────
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [onClose, inputRef]);

  // ─── Navigation helpers ────────────────────────────────────────────
  const getItemAtIndex = useCallback(
    (index: number): { type: 'product' | 'category'; slug: string } | null => {
      const productCount = products.slice(0, 5).length;
      if (index < productCount) {
        return { type: 'product', slug: products[index]?.slug ?? '' };
      }
      const catIndex = index - productCount;
      if (catIndex < categories.slice(0, 5).length) {
        return { type: 'category', slug: categories[catIndex]?.slug ?? '' };
      }
      return null;
    },
    [products, categories]
  );

  const handleSelectProduct = useCallback(
    (slug: string) => {
      onSelect(slug);
      router.push(`/products/${slug}`);
    },
    [onSelect, router]
  );

  const handleSelectCategory = useCallback(
    (slug: string) => {
      onSelect(slug);
      router.push(`/products/category/${slug}`);
    },
    [onSelect, router]
  );

  // ─── Keyboard navigation ──────────────────────────────────────────
  useEffect(() => {
    const input = inputRef.current;
    if (!input || !isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setActiveIndex((prev) => (prev < totalItems - 1 ? prev + 1 : 0));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setActiveIndex((prev) => (prev > 0 ? prev - 1 : totalItems - 1));
      } else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        const item = getItemAtIndex(activeIndex);
        if (item?.type === 'product') handleSelectProduct(item.slug);
        else if (item?.type === 'category') handleSelectCategory(item.slug);
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    input.addEventListener('keydown', handleKeyDown);
    return () => input.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, activeIndex, totalItems, getItemAtIndex, handleSelectProduct, handleSelectCategory, onClose, inputRef]);

  // ─── Render ────────────────────────────────────────────────────────
  if (!isOpen || query.length < 2) return null;

  const productCount = products.slice(0, 5).length;

  return (
    <div
      ref={containerRef}
      role="listbox"
      aria-label="Search suggestions"
      className={cn(
        'absolute left-0 right-0 top-full z-50 mt-1 max-h-[400px] overflow-y-auto',
        'rounded-lg border border-gray-200 bg-white shadow-lg',
        'dark:border-gray-700 dark:bg-gray-800'
      )}
    >
      {isLoading ? (
        <SuggestionsLoading />
      ) : products.length === 0 && categories.length === 0 ? (
        <p className="px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
          No results found for &ldquo;{query}&rdquo;
        </p>
      ) : (
        <div className="py-1">
          <ProductSuggestions
            products={products}
            query={query}
            activeIndex={activeIndex}
            baseIndex={0}
            onSelect={handleSelectProduct}
          />
          {products.length > 0 && categories.length > 0 && (
            <hr className="my-1 border-gray-200 dark:border-gray-700" />
          )}
          <CategorySuggestions
            categories={categories}
            query={query}
            activeIndex={activeIndex}
            baseIndex={productCount}
            onSelect={handleSelectCategory}
          />
        </div>
      )}
    </div>
  );
};

export default Autocomplete;
