export default function ProductVariantsLoading() {
  return (
    <div className="animate-pulse space-y-6">
      {/* Back Link */}
      <div className="h-4 w-32 rounded bg-gray-200 dark:bg-gray-700" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="h-7 w-40 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="mt-1 h-4 w-64 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="h-10 w-36 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900"
          >
            <div className="mb-1 h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-8 w-12 rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
      </div>

      {/* Option Types */}
      <div className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900">
        <div className="mb-4 flex items-center justify-between">
          <div className="h-6 w-28 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-5 w-20 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        {Array.from({ length: 2 }).map((_, i) => (
          <div key={i} className="mb-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="mt-1 h-3 w-32 rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
      </div>

      {/* Variants Table */}
      <div className="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
        <div className="border-b border-gray-200 p-4 dark:border-gray-700">
          <div className="h-6 w-20 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="p-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div
              key={i}
              className="flex items-center gap-4 border-b border-gray-200 py-3 last:border-0 dark:border-gray-700"
            >
              <div className="h-10 w-10 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-4 w-20 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-4 w-16 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-4 w-12 rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-5 w-16 rounded-full bg-gray-200 dark:bg-gray-700" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
