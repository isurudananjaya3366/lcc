export default function SearchLoading() {
  return (
    <div className="space-y-6">
      {/* Heading skeleton */}
      <div className="h-8 w-64 animate-pulse rounded-md bg-gray-200 dark:bg-gray-800" />

      {/* Search input skeleton */}
      <div className="h-12 w-full max-w-xl animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800" />

      {/* Results grid skeleton */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-800">
            {/* Image skeleton */}
            <div className="aspect-square w-full animate-pulse rounded-md bg-gray-200 dark:bg-gray-800" />
            {/* Title skeleton */}
            <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-800" />
            {/* Price skeleton */}
            <div className="h-4 w-1/3 animate-pulse rounded bg-gray-200 dark:bg-gray-800" />
            {/* Button skeleton */}
            <div className="h-10 w-full animate-pulse rounded-md bg-gray-200 dark:bg-gray-800" />
          </div>
        ))}
      </div>
    </div>
  );
}
