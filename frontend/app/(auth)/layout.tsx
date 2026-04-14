import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { AuthFooter } from '@/components/auth/AuthFooter';
import { AuthLogo } from '@/components/auth/AuthLogo';

export const metadata: Metadata = {
  title: {
    template: '%s | LankaCommerce Cloud',
    default: 'Authentication',
  },
  description:
    'Secure authentication for LankaCommerce Cloud — multi-tenant ERP system for Sri Lankan SMEs.',
  openGraph: {
    title: 'Authentication | LankaCommerce Cloud',
    description: 'Sign in or create an account to access LankaCommerce Cloud ERP.',
    type: 'website',
    siteName: 'LankaCommerce Cloud',
  },
  twitter: {
    card: 'summary',
    title: 'Authentication | LankaCommerce Cloud',
    description: 'Sign in or create an account to access LankaCommerce Cloud ERP.',
  },
  robots: {
    index: false,
    follow: false,
  },
};

/**
 * Authentication layout.
 * Wraps login, register, and password-reset pages with a centered card design.
 */
export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-4 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 md:p-6 lg:p-8">
      {/* Subtle background pattern */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%234f46e5' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
        }}
        aria-hidden="true"
      />

      {/* Header — Logo */}
      <div className="relative z-10 mb-8 py-4">
        <AuthLogo size="lg" />
      </div>

      {/* Content */}
      <main className="relative z-10 flex w-full flex-grow items-start justify-center sm:items-center">
        {children}
      </main>

      {/* Footer */}
      <div className="relative z-10 mt-8 py-4">
        <AuthFooter />
      </div>
    </div>
  );
}
