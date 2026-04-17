'use client';

import { cn } from '@/lib/utils';
import { NoResultsIllustration } from './NoResultsIllustration';
import { NoResultsSuggestions } from './NoResultsSuggestions';
import { PopularProductsFallback } from './PopularProductsFallback';

interface NoResultsStateProps {
  query: string;
  onSuggestionClick?: (suggestion: string) => void;
  className?: string;
}

const POPULAR_CATEGORIES = [
  { label: 'Electronics', href: '/store/category/electronics' },
  { label: 'Clothing', href: '/store/category/clothing' },
  { label: 'Home & Garden', href: '/store/category/home-garden' },
  { label: 'Sports', href: '/store/category/sports' },
];

export function NoResultsState({
  query,
  onSuggestionClick,
  className,
}: NoResultsStateProps) {
  return (
    <div
      className={cn('flex flex-col items-center gap-6 py-12', className)}
      role="region"
      aria-label="No search results"
    >
      <NoResultsIllustration />

      <div className="text-center">
        <h2 className="text-lg font-semibold text-foreground">
          No results found for &lsquo;{query}&rsquo;
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Try different keywords or remove some filters
        </p>
      </div>

      <NoResultsSuggestions className="w-full max-w-md" />

      <div className="w-full max-w-md">
        <h3 className="mb-2 text-sm font-semibold text-foreground">
          Popular categories
        </h3>
        <div className="flex flex-wrap gap-2">
          {POPULAR_CATEGORIES.map((cat) => (
            <button
              key={cat.label}
              type="button"
              onClick={() => onSuggestionClick?.(cat.label)}
              className="rounded-full border border-border bg-background px-3 py-1 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      <PopularProductsFallback className="w-full" />
    </div>
  );
}
