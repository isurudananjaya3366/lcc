export default function ProductsLoading() {
  return (
    <div className="animate-pulse space-y-6">
      {/* Header Skeleton */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-7 w-32 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="mt-2 h-4 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="h-10 w-36 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>

      {/* Filters Skeleton */}
      <div className="flex gap-3">
        <div className="h-10 flex-1 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-36 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>

      {/* Table Skeleton */}
      <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
        {/* Table Header */}
        <div className="flex items-center gap-4 border-b border-gray-200 px-4 py-3 dark:border-gray-700">
          <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-20 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        {/* Table Rows */}
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center gap-4 border-b border-gray-200 px-4 py-4 last:border-0 dark:border-gray-700"
          >
            <div className="h-4 w-20 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 w-40 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-4 w-20 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-5 w-16 rounded-full bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
      </div>

      {/* Pagination Skeleton */}
      <div className="flex items-center justify-between">
        <div className="h-4 w-32 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="flex gap-2">
          <div className="h-9 w-20 rounded-lg bg-gray-200 dark:bg-gray-700" />
          <div className="h-9 w-20 rounded-lg bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    </div>
  );
}
