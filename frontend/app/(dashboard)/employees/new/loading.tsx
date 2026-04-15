export default function NewEmployeeLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="h-8 w-40 rounded bg-gray-200 dark:bg-gray-700" />
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 w-24 rounded bg-gray-200 dark:bg-gray-700" />
            <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        ))}
      </div>
      <div className="flex justify-end gap-2">
        <div className="h-10 w-24 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-32 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
    </div>
  );
}
