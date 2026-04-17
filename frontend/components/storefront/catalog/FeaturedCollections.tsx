import Link from 'next/link';
import { cn } from '@/lib/utils';
import { CollectionCard } from './CollectionCard';
import type { CollectionCardData } from './CollectionCard';

interface FeaturedCollectionsProps {
  collections: CollectionCardData[];
  title?: string;
  subtitle?: string;
  limit?: number;
  className?: string;
}

export function FeaturedCollections({
  collections,
  title = 'Featured Collections',
  subtitle,
  limit = 4,
  className,
}: FeaturedCollectionsProps) {
  const displayed = collections.slice(0, limit);

  if (!displayed.length) return null;

  return (
    <section className={cn('w-full py-10 sm:py-14', className)}>
      {/* Section header */}
      <div className="mb-6 flex items-end justify-between sm:mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 sm:text-3xl">{title}</h2>
          {subtitle && <p className="mt-1 text-base text-gray-600 sm:text-lg">{subtitle}</p>}
        </div>

        <Link
          href="/products"
          className="hidden items-center gap-1 text-sm font-medium text-blue-600 transition-colors hover:text-blue-800 sm:inline-flex"
        >
          View all
          {/* Arrow right icon */}
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
            />
          </svg>
        </Link>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {displayed.map((collection) => (
          <CollectionCard key={collection.id} collection={collection} />
        ))}
      </div>

      {/* Mobile "View All" */}
      <div className="mt-6 text-center sm:hidden">
        <Link
          href="/products"
          className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800"
        >
          View all collections
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M13.5 4.5 21 12m0 0-7.5 7.5M21 12H3"
            />
          </svg>
        </Link>
      </div>
    </section>
  );
}
