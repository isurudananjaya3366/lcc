export default function ProductsLoading() {
  return (
    <div className="py-8">
      {/* Header skeleton */}
      <div className="border-b pb-6 mb-8">
        {/* Breadcrumb placeholder */}
        <div className="mb-4 flex items-center gap-2">
          <div className="h-4 w-16 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-4 animate-pulse rounded bg-gray-200" />
          <div className="h-4 w-24 animate-pulse rounded bg-gray-200" />
        </div>
        {/* Title placeholder */}
        <div className="h-9 w-48 animate-pulse rounded bg-gray-200 mb-2" />
        {/* Count placeholder */}
        <div className="h-5 w-28 animate-pulse rounded bg-gray-200" />
      </div>

      {/* Content skeleton: sidebar + grid */}
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 lg:gap-8">
        {/* Sidebar skeleton */}
        <div className="hidden lg:block">
          <div className="rounded-lg border bg-white p-6 space-y-4">
            <div className="h-6 w-24 animate-pulse rounded bg-gray-200" />
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-4 w-full animate-pulse rounded bg-gray-200" />
              ))}
            </div>
          </div>
        </div>

        {/* Grid skeleton */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={i}
              className="h-72 animate-pulse rounded-lg bg-gray-200"
            />
          ))}
        </div>
      </div>
    </div>
  );
}
