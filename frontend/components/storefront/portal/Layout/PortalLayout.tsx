'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStoreAuthStore } from '@/stores/store';
import { PortalSidebar } from './PortalSidebar';
import { PortalHeader } from './PortalHeader';

export function PortalLayout({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useStoreAuthStore((s) => s.isAuthenticated);
  const isLoading = useStoreAuthStore((s) => s.isLoading);
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/account/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex min-h-screen">
      {/* Desktop sidebar */}
      <aside className="hidden w-64 shrink-0 border-r bg-card lg:block">
        <PortalSidebar />
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col">
        <PortalHeader />
        <main className="flex-1 p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
