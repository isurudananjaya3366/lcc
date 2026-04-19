import Link from 'next/link';

export function PageNotFound() {
  return (
    <div className="max-w-4xl mx-auto py-16 px-4 text-center">
      <h1 className="text-4xl font-bold tracking-tight">Page Not Found</h1>
      <p className="mt-4 text-lg text-muted-foreground">
        The page you are looking for does not exist or has been moved.
      </p>
      <Link
        href="/"
        className="mt-8 inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
      >
        Back to Home
      </Link>
    </div>
  );
}
