export default function PayslipDetailsLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="h-8 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="h-20 rounded-lg bg-gray-200 dark:bg-gray-700" />
        <div className="h-20 rounded-lg bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-8 w-full rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      <div className="h-16 rounded-lg bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
