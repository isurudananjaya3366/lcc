export default function CustomerDetailsLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-5 w-32 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="flex gap-2">
          <div className="h-10 w-20 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-10 w-20 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      {/* Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-24 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      {/* Tabs */}
      <div className="flex gap-4 border-b">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      {/* Content */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="h-48 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-48 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>
    </div>
  );
}
