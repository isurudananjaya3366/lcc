export default function EmployeeDetailsLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center gap-4">
        <div className="h-20 w-20 rounded-full bg-gray-200 dark:bg-gray-700" />
        <div className="space-y-2">
          <div className="h-6 w-40 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-28 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-12 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
