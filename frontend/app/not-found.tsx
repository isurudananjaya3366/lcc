import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center font-[family-name:var(--font-inter)]">
      <h1 className="text-8xl font-bold text-gray-900">404</h1>
      <h2 className="mt-2 text-xl font-medium text-gray-700">
        Page Not Found
      </h2>
      <p className="mt-2 text-gray-500">
        The page you&apos;re looking for doesn&apos;t exist or has been moved.
      </p>
      <nav className="mt-6 flex gap-4" aria-label="Quick navigation">
        <Link
          href="/"
          className="rounded-md bg-blue-600 px-5 py-2.5 text-white hover:bg-blue-700"
        >
          Back to Home
        </Link>
        <Link
          href="/dashboard"
          className="rounded-md border border-gray-300 px-5 py-2.5 text-gray-700 hover:bg-gray-50"
        >
          Dashboard
        </Link>
      </nav>
    </main>
  );
}
