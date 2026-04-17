import type { Metadata } from 'next';
import { SearchForm } from '@/components/storefront/search/SearchInput';
import { SearchResultsContainer } from '@/components/storefront/search/SearchResults';

// ─── Types ──────────────────────────────────────────────────────────────────

interface SearchPageProps {
  searchParams: Promise<{
    q?: string;
    category?: string;
    sort?: string;
    page?: string;
    min_price?: string;
    max_price?: string;
  }>;
}

// ─── Dynamic Metadata ───────────────────────────────────────────────────────

export async function generateMetadata({
  searchParams,
}: SearchPageProps): Promise<Metadata> {
  const params = await searchParams;
  const query = params.q?.trim();

  if (query) {
    return {
      title: `Search: ${query} | LankaCommerce Store`,
      description: `Search results for "${query}" on LankaCommerce Store.`,
      robots: { index: false, follow: false },
    };
  }

  return {
    title: 'Search Products | LankaCommerce Store',
    description: 'Search for products across all categories.',
    robots: { index: false, follow: false },
  };
}

// ─── Page Component ─────────────────────────────────────────────────────────

/**
 * Search results page with filtering & sorting.
 * Accepts query parameters: q, category, sort, page, min_price, max_price.
 */
export default async function SearchPage({ searchParams }: SearchPageProps) {
  const params = await searchParams;
  const query = params.q?.trim() || '';
  const category = params.category || '';
  const sort = params.sort || '';
  const page = params.page || '1';
  const minPrice = params.min_price || '';
  const maxPrice = params.max_price || '';

  return (
    <div className="space-y-6">
      {/* Page heading */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">
          {query ? (
            <>
              Results for &lsquo;<span className="text-green-600 dark:text-green-400">{query}</span>&rsquo;
            </>
          ) : (
            'Search Products'
          )}
        </h1>
        {query && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Showing results matching your search
          </p>
        )}
      </div>

      {/* Search form */}
      <SearchForm initialQuery={query} size="lg" />

      {/* Search results */}
      <SearchResultsContainer
        query={query}
        category={category}
        sort={sort}
        page={page}
        minPrice={minPrice}
        maxPrice={maxPrice}
      />
    </div>
  );
}
