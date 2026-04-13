import Link from 'next/link';
import type { ReactNode } from 'react';

/**
 * Authentication layout.
 * Wraps login, register, and password-reset pages with a centered card design.
 */
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4 md:p-6 lg:p-8">
      {/* Header */}
      <div className="mb-8 text-center">
        <Link href="/" className="inline-block">
          <h1 className="text-2xl font-bold text-gray-900">
            LankaCommerce Cloud
          </h1>
        </Link>
        <p className="mt-1 text-sm text-gray-500">
          Multi-tenant ERP for Sri Lankan SMEs
        </p>
      </div>

      {/* Content Card */}
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-lg">
        {children}
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-sm text-gray-600">
        <div className="mb-2 flex justify-center gap-4">
          <Link href="/help" className="hover:text-gray-900">Help</Link>
          <Link href="/privacy" className="hover:text-gray-900">Privacy</Link>
          <Link href="/terms" className="hover:text-gray-900">Terms</Link>
        </div>
        <p>&copy; {new Date().getFullYear()} LankaCommerce. All rights reserved.</p>
      </footer>
    </div>
  );
}
