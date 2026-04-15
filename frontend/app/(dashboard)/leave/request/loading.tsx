export default function LeaveRequestLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="h-8 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      <div className="space-y-4 max-w-xl">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
        <div className="h-24 w-full rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    </div>
  );
}
