/**
 * Storefront loading skeleton — shown during page transitions.
 * Provides visual feedback with accessible attributes.
 */
export default function StorefrontLoading() {
  return (
    <div role="status" aria-label="Loading store content" className="animate-pulse">
      {/* Hero skeleton */}
      <div className="bg-gray-200 h-64 md:h-96 w-full" />

      {/* Content skeleton */}
      <div className="container mx-auto px-4 py-8">
        {/* Section title skeleton */}
        <div className="h-8 bg-gray-200 rounded w-48 mb-6" />

        {/* Product grid skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="space-y-3">
              {/* Image placeholder */}
              <div className="bg-gray-200 rounded-lg aspect-square w-full" />
              {/* Title placeholder */}
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              {/* Price placeholder */}
              <div className="h-4 bg-gray-200 rounded w-1/4" />
            </div>
          ))}
        </div>
      </div>

      <span className="sr-only">Loading store content...</span>
    </div>
  );
}
