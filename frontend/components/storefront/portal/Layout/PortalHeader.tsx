'use client';

import { useStoreAuthStore } from '@/stores/store';
import { MobileNavDrawer } from './MobileNavDrawer';

export function PortalHeader() {
  const user = useStoreAuthStore((s) => s.user);

  const greeting = user?.firstName
    ? `Welcome back, ${user.firstName}`
    : 'My Account';

  return (
    <header className="flex items-center gap-4 border-b px-4 py-3 lg:px-6">
      <MobileNavDrawer />
      <h1 className="text-lg font-semibold">{greeting}</h1>
    </header>
  );
}
