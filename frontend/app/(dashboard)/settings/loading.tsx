export default function SettingsLoading() {
  return (
    <div className="animate-pulse space-y-6" aria-busy="true">
      <div className="space-y-2">
        <div className="h-8 w-48 rounded bg-gray-200 dark:bg-gray-700" />
        <div className="h-4 w-72 rounded bg-gray-200 dark:bg-gray-700" />
      </div>
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="h-32 rounded-lg border bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    </div>
  );
}
