import Link from 'next/link';

export default function ProductNotFound() {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center py-16 text-center">
      <svg
        className="mb-4 h-16 w-16 text-gray-300"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1}
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z"
        />
      </svg>
      <h2 className="mb-2 text-2xl font-semibold text-gray-900">
        Product Not Found
      </h2>
      <p className="mb-6 max-w-md text-sm text-gray-600">
        The product you&apos;re looking for doesn&apos;t exist or may have been removed.
        Try searching for it or browse our catalog.
      </p>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Link
          href="/products"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Browse Products
        </Link>
        <Link
          href="/"
          className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Go Home
        </Link>
      </div>
    </div>
  );
}
