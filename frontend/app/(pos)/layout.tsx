import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { SessionProvider } from '@/components/auth/SessionProvider';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export const metadata: Metadata = {
  title: {
    template: '%s | POS Terminal - LCC',
    default: 'POS Terminal - LCC',
  },
  description: 'Point of Sale terminal for LankaCommerce Cloud retail transactions.',
  robots: {
    index: false,
    follow: false,
  },
};

export default function POSLayout({ children }: { children: ReactNode }) {
  return (
    <SessionProvider>
      <ProtectedRoute>
        <div className="flex h-screen w-screen flex-col overflow-hidden bg-gray-100 dark:bg-gray-950">
          {children}
        </div>
      </ProtectedRoute>
    </SessionProvider>
  );
}
