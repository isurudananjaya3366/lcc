'use client';

import React, { type FC } from 'react';
import CategorySuggestionItem from './CategorySuggestionItem';
import type { SearchCategory } from '@/services/storefront/searchService';

export interface CategorySuggestionsProps {
  categories: SearchCategory[];
  query: string;
  activeIndex: number;
  baseIndex: number;
  onSelect: (slug: string) => void;
}

const CategorySuggestions: FC<CategorySuggestionsProps> = ({
  categories,
  query,
  activeIndex,
  baseIndex,
  onSelect,
}) => {
  if (categories.length === 0) return null;

  return (
    <div role="group" aria-label="Category suggestions">
      <p className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
        Categories
      </p>
      {categories.slice(0, 5).map((category, i) => (
        <CategorySuggestionItem
          key={category.id ?? category.slug}
          category={category}
          query={query}
          isActive={activeIndex === baseIndex + i}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
};

export default CategorySuggestions;
