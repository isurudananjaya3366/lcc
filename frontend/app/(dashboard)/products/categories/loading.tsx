export default function CategoriesLoading() {
  return (
    <div className="animate-pulse space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-7 w-28 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="mt-2 h-4 w-56 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>

      {/* Search */}
      <div className="flex gap-3">
        <div className="h-10 flex-1 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>

      {/* Category Tree */}
      <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
        <div className="border-b border-gray-200 px-4 py-3 dark:border-gray-700">
          <div className="h-4 w-32 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-3 px-4 py-3"
              style={{ paddingLeft: `${(i % 3) * 24 + 16}px` }}
            >
              <div className="h-4 w-4 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-4 w-32 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="ml-auto h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
            </div>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
          >
            <div className="mb-1 h-4 w-28 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-8 w-8 rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
      </div>
    </div>
  );
}
