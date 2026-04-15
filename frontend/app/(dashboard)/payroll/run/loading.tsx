export default function PayrollRunLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="h-8 w-36 rounded bg-gray-200 dark:bg-gray-700" />
      <div className="flex gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-10 w-28 rounded-full bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
      <div className="h-64 rounded-lg bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
