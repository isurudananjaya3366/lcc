export default function AuditLogLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-4 w-72 rounded bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
      <div className="flex gap-4">
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-40 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-10 w-48 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="h-80 rounded-lg border bg-gray-200 dark:bg-gray-700" />
    </div>
  );
}
