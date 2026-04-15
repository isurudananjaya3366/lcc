export default function OrgChartLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
      <div className="flex flex-col items-center gap-8">
        <div className="h-24 w-48 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="flex gap-8">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-20 w-40 rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
        <div className="flex gap-6">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-16 w-32 rounded-lg bg-gray-200 dark:bg-gray-700" />
          ))}
        </div>
      </div>
    </div>
  );
}
