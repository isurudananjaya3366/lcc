import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import { SessionProvider } from '@/components/auth/SessionProvider';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

export const metadata: Metadata = {
  title: {
    template: '%s | POS-ERP System',
    default: 'Dashboard | POS-ERP System',
  },
  robots: {
    index: false,
    follow: false,
  },
};

/**
 * Dashboard route-group layout.
 *
 * Server component shell that wraps all protected ERP pages with:
 *  1. SessionProvider   — session-expiry monitoring
 *  2. ProtectedRoute    — auth gate + permission checks
 *  3. DashboardLayout   — CSS Grid sidebar/header/content
 */
export default function Layout({ children }: { children: ReactNode }) {
  return (
    <SessionProvider>
      <ProtectedRoute>
        <DashboardLayout>{children}</DashboardLayout>
      </ProtectedRoute>
    </SessionProvider>
  );
}
