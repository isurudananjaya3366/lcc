import type { Metadata } from 'next';
import Link from 'next/link';
import { ShieldX } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Unauthorized',
  description: 'You do not have permission to access this page.',
};

export default function UnauthorizedPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md text-center">
        <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-red-100">
          <ShieldX className="h-10 w-10 text-red-500" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Access Denied</h1>
        <p className="mt-3 text-sm text-gray-500">
          You don&apos;t have permission to access this page. Contact your administrator if you
          believe this is an error.
        </p>
        <div className="mt-8 flex flex-col items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Go to Dashboard
          </Link>
          <Link href="/login" className="text-sm text-gray-500 underline hover:text-gray-700">
            Sign in with a different account
          </Link>
        </div>
      </div>
    </div>
  );
}
