'use client';

import { cn } from '@/lib/utils';
import { NoResultsIllustration } from './NoResultsIllustration';
import Link from 'next/link';

interface EmptyQueryStateProps {
  className?: string;
}

const POPULAR_SEARCHES = [
  'Laptop',
  'Headphones',
  'T-shirt',
  'Running shoes',
  'Phone case',
];

const FEATURED_CATEGORIES = [
  { label: 'Electronics', href: '/store/category/electronics' },
  { label: 'Clothing', href: '/store/category/clothing' },
  { label: 'Home & Garden', href: '/store/category/home-garden' },
  { label: 'Sports & Outdoors', href: '/store/category/sports' },
  { label: 'Books', href: '/store/category/books' },
];

export function EmptyQueryState({ className }: EmptyQueryStateProps) {
  return (
    <div
      className={cn('flex flex-col items-center gap-6 py-12', className)}
      role="region"
      aria-label="Search start"
    >
      <NoResultsIllustration className="opacity-50" />

      <div className="text-center">
        <h2 className="text-lg font-semibold text-foreground">
          Start Your Search
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Enter a search term to find products
        </p>
      </div>

      <div className="w-full max-w-md">
        <h3 className="mb-2 text-sm font-semibold text-foreground">
          Popular searches
        </h3>
        <div className="flex flex-wrap gap-2">
          {POPULAR_SEARCHES.map((term) => (
            <Link
              key={term}
              href={`/store/search?q=${encodeURIComponent(term)}`}
              className="rounded-full border border-border bg-background px-3 py-1 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {term}
            </Link>
          ))}
        </div>
      </div>

      <div className="w-full max-w-md">
        <h3 className="mb-2 text-sm font-semibold text-foreground">
          Featured categories
        </h3>
        <div className="flex flex-wrap gap-2">
          {FEATURED_CATEGORIES.map((cat) => (
            <Link
              key={cat.label}
              href={cat.href}
              className="rounded-full border border-border bg-background px-3 py-1 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {cat.label}
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
