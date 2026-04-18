'use client';

import { usePathname } from 'next/navigation';
import { OrderSidebar, CollapsibleSidebar } from '@/components/storefront/checkout';

export function CheckoutSidebarWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isConfirmation = pathname?.includes('/checkout/confirmation');

  if (isConfirmation) {
    return <>{children}</>;
  }

  return (
    <>
      {/* Mobile collapsible sidebar */}
      <div className="mb-6 lg:hidden">
        <CollapsibleSidebar />
      </div>

      {/* Desktop two-column layout */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_380px]">
        <div>{children}</div>
        <aside className="hidden lg:block">
          <OrderSidebar />
        </aside>
      </div>
    </>
  );
}
