import Link from 'next/link';

/**
 * Storefront 404 page — shown when a storefront route is not found.
 */
export default function StorefrontNotFound() {
  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <div className="max-w-md mx-auto">
        <h2 className="text-6xl font-bold text-gray-300 mb-4">404</h2>
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h3>
        <p className="text-gray-600 mb-6">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/"
            className="rounded-lg bg-green-600 px-6 py-2 text-white font-medium hover:bg-green-700 transition-colors"
          >
            Go Home
          </Link>
          <Link
            href="/products"
            className="rounded-lg border border-gray-300 px-6 py-2 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
          >
            Browse Products
          </Link>
        </div>
      </div>
    </div>
  );
}
