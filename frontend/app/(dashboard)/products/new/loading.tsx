export default function ProductNewLoading() {
  return (
    <div className="animate-pulse space-y-6">
      {/* Back Link */}
      <div className="h-4 w-32 rounded bg-gray-200 dark:bg-gray-700" />

      {/* Title */}
      <div className="h-7 w-40 rounded bg-gray-200 dark:bg-gray-700" />

      {/* Form Sections */}
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="rounded-lg border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900"
        >
          <div className="mb-4 h-6 w-36 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="grid gap-4 sm:grid-cols-2">
            {Array.from({ length: 4 }).map((_, j) => (
              <div key={j}>
                <div className="mb-1 h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
                <div className="h-10 w-full rounded-lg bg-gray-200 dark:bg-gray-700" />
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Actions */}
      <div className="flex gap-3 border-t border-gray-200 pt-6 dark:border-gray-700">
        <div className="h-10 w-24 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>
    </div>
  );
}
