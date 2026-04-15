import type { Metadata } from 'next';

interface SearchParams {
  q?: string;
  category?: string;
  sort?: string;
  page?: string;
  min_price?: string;
  max_price?: string;
}

export const metadata: Metadata = {
  title: 'Search Products',
  description: 'Search for products across all categories.',
};

/**
 * Search results page with filtering & sorting.
 * Accepts query parameters: q, category, sort, page, min_price, max_price.
 * Will be fully implemented in SubPhase-05.
 */
export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const params = await searchParams;
  const query = params.q || '';

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">
        {query ? `Search results for "${query}"` : 'Search Products'}
      </h1>

      {/* Search input */}
      <div className="mb-8">
        <form action="/search" method="GET">
          <div className="flex gap-2 max-w-xl">
            <input
              type="search"
              name="q"
              defaultValue={query}
              placeholder="Search for products..."
              className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
              aria-label="Search products"
            />
            <button
              type="submit"
              className="rounded-lg bg-green-600 px-6 py-2 text-white font-medium hover:bg-green-700 transition-colors"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Results placeholder */}
      <p className="text-muted-foreground">
        Search results and filtering will be implemented in SubPhase-05.
      </p>
    </div>
  );
}
