export default function VendorDetailsLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-5 w-24 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
        <div className="flex gap-2">
          <div className="h-10 w-20 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-10 w-20 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      {/* Tabs */}
      <div className="flex gap-4 border-b">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-10 w-28 rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      {/* Content */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="h-48 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-48 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>
      {/* Table */}
      <div className="space-y-3">
        <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-12 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
