export default function RolesLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-72 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="h-10 w-32 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-40 rounded-lg border bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
