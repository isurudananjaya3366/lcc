export default function POSLoading() {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center bg-gray-100 dark:bg-gray-950">
      <div
        className="h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-primary motion-reduce:animate-none"
        role="status"
      >
        <span className="sr-only">Loading POS Terminal...</span>
      </div>
      <p className="mt-4 text-lg font-medium text-gray-600 dark:text-gray-400">
        Loading POS Terminal...
      </p>
    </div>
  );
}
