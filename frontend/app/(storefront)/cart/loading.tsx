export default function CartLoading() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div className="h-9 w-48 rounded bg-muted" />

      {/* Cart items skeleton */}
      <div className="space-y-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div
            key={i}
            className="flex gap-4 rounded-lg border border-border p-4"
          >
            <div className="h-24 w-24 shrink-0 rounded-md bg-muted" />
            <div className="flex flex-1 flex-col justify-between">
              <div className="space-y-2">
                <div className="h-5 w-40 rounded bg-muted" />
                <div className="h-4 w-24 rounded bg-muted" />
              </div>
              <div className="flex items-center justify-between">
                <div className="h-8 w-28 rounded bg-muted" />
                <div className="h-5 w-20 rounded bg-muted" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary skeleton */}
      <div className="ml-auto w-full max-w-sm space-y-3 rounded-lg border border-border p-6">
        <div className="flex justify-between">
          <div className="h-4 w-20 rounded bg-muted" />
          <div className="h-4 w-16 rounded bg-muted" />
        </div>
        <div className="flex justify-between">
          <div className="h-4 w-16 rounded bg-muted" />
          <div className="h-4 w-16 rounded bg-muted" />
        </div>
        <div className="flex justify-between">
          <div className="h-4 w-12 rounded bg-muted" />
          <div className="h-4 w-16 rounded bg-muted" />
        </div>
        <div className="border-t border-border pt-3">
          <div className="flex justify-between">
            <div className="h-5 w-14 rounded bg-muted" />
            <div className="h-5 w-24 rounded bg-muted" />
          </div>
        </div>
        <div className="h-10 w-full rounded-md bg-muted" />
      </div>
    </div>
  );
}
