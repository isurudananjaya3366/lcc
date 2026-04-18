'use client';

import { User, LogIn } from 'lucide-react';
import Link from 'next/link';

interface GuestCheckoutCheckProps {
  isAuthenticated?: boolean;
  children: React.ReactNode;
}

export const GuestCheckoutCheck = ({
  isAuthenticated = false,
  children,
}: GuestCheckoutCheckProps) => {
  if (isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div>
      <div className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4">
        <div className="flex items-start gap-3">
          <User className="mt-0.5 h-5 w-5 text-blue-600" />
          <div className="flex-1">
            <p className="text-sm font-medium text-blue-900">Checking out as a guest</p>
            <p className="mt-1 text-sm text-blue-700">
              You can continue without an account, or{' '}
              <Link
                href="/login?redirect=/checkout/information"
                className="inline-flex items-center gap-1 font-medium underline hover:no-underline"
              >
                <LogIn className="h-3.5 w-3.5" />
                sign in
              </Link>{' '}
              for a faster checkout experience.
            </p>
          </div>
        </div>
      </div>
      {children}
    </div>
  );
};
