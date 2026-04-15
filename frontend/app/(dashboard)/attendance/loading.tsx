export default function AttendanceLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-36 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-28 rounded-lg bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      <div className="h-80 rounded-lg bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
