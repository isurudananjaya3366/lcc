export default function ProductDetailLoading() {
  return (
    <div className="py-6">
      {/* Breadcrumb skeleton */}
      <div className="mb-6 flex items-center gap-2">
        <div className="h-4 w-12 animate-pulse rounded bg-gray-200" />
        <div className="h-4 w-4 animate-pulse rounded bg-gray-200" />
        <div className="h-4 w-20 animate-pulse rounded bg-gray-200" />
        <div className="h-4 w-4 animate-pulse rounded bg-gray-200" />
        <div className="h-4 w-32 animate-pulse rounded bg-gray-200" />
      </div>

      {/* Two-column layout skeleton */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 lg:gap-12">
        {/* Image gallery skeleton */}
        <div>
          <div className="aspect-square w-full animate-pulse rounded-lg bg-gray-200" />
          {/* Thumbnails */}
          <div className="mt-4 flex gap-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-16 w-16 animate-pulse rounded bg-gray-200" />
            ))}
          </div>
        </div>

        {/* Product info skeleton */}
        <div className="space-y-4">
          {/* Title */}
          <div className="h-8 w-3/4 animate-pulse rounded bg-gray-200" />
          {/* Price */}
          <div className="h-7 w-32 animate-pulse rounded bg-gray-200" />
          {/* Rating */}
          <div className="h-5 w-40 animate-pulse rounded bg-gray-200" />
          {/* SKU */}
          <div className="h-4 w-24 animate-pulse rounded bg-gray-200" />
          {/* Description lines */}
          <div className="space-y-2 pt-2">
            <div className="h-4 w-full animate-pulse rounded bg-gray-200" />
            <div className="h-4 w-full animate-pulse rounded bg-gray-200" />
            <div className="h-4 w-2/3 animate-pulse rounded bg-gray-200" />
          </div>
          {/* Stock badge */}
          <div className="h-6 w-20 animate-pulse rounded-full bg-gray-200" />
          {/* Action buttons */}
          <div className="flex gap-3 pt-4">
            <div className="h-12 flex-1 animate-pulse rounded-lg bg-gray-200" />
            <div className="h-12 w-12 animate-pulse rounded-lg bg-gray-200" />
          </div>
        </div>
      </div>

      {/* Tabs skeleton */}
      <div className="mt-12 border-t pt-8">
        <div className="flex gap-4 mb-6">
          <div className="h-8 w-24 animate-pulse rounded bg-gray-200" />
          <div className="h-8 w-24 animate-pulse rounded bg-gray-200" />
          <div className="h-8 w-24 animate-pulse rounded bg-gray-200" />
        </div>
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-4 w-full animate-pulse rounded bg-gray-200" />
          ))}
        </div>
      </div>

      {/* Related products skeleton */}
      <div className="mt-12 border-t pt-8">
        <div className="h-6 w-40 animate-pulse rounded bg-gray-200 mb-4" />
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-64 animate-pulse rounded-lg bg-gray-200" />
          ))}
        </div>
      </div>
    </div>
  );
}
