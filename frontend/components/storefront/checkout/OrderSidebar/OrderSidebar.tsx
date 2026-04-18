'use client';

import { useStoreCartStore } from '@/stores/store';
import SidebarItemsList from './SidebarItemsList';
import SidebarSubtotal from './SidebarSubtotal';
import SidebarShipping from './SidebarShipping';
import SidebarDiscount from './SidebarDiscount';
import SidebarTotal from './SidebarTotal';

export default function OrderSidebar() {
  const itemCount = useStoreCartStore((s) => s.getItemCount());
  const isLoading = useStoreCartStore((s) => s.isLoading);

  return (
    <div className="sticky top-24 w-full rounded-lg bg-gray-50 p-5 shadow-sm">
      {/* Header */}
      <div className="mb-4 flex items-center gap-2">
        <h2 className="text-lg font-semibold text-gray-900">Order Summary</h2>
        {itemCount > 0 && (
          <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-gray-800 px-1.5 text-[11px] font-medium text-white">
            {itemCount}
          </span>
        )}
      </div>

      {/* Loading skeleton */}
      {isLoading ? (
        <div className="space-y-3 animate-pulse">
          {[1, 2].map((i) => (
            <div key={i} className="flex items-center gap-3">
              <div className="h-12 w-12 rounded-md bg-gray-200" />
              <div className="flex-1 space-y-1.5">
                <div className="h-3.5 w-3/4 rounded bg-gray-200" />
                <div className="h-3 w-1/2 rounded bg-gray-200" />
              </div>
            </div>
          ))}
          <div className="space-y-2 pt-3 border-t border-gray-200">
            <div className="flex justify-between">
              <div className="h-3.5 w-16 rounded bg-gray-200" />
              <div className="h-3.5 w-20 rounded bg-gray-200" />
            </div>
            <div className="flex justify-between">
              <div className="h-3.5 w-14 rounded bg-gray-200" />
              <div className="h-3.5 w-20 rounded bg-gray-200" />
            </div>
            <div className="flex justify-between pt-2 border-t border-gray-200">
              <div className="h-4 w-12 rounded bg-gray-200" />
              <div className="h-5 w-24 rounded bg-gray-200" />
            </div>
          </div>
        </div>
      ) : (
        <>
          <SidebarItemsList />

          <div className="mt-4 space-y-0.5 border-t border-gray-200 pt-3">
            <SidebarSubtotal />
            <SidebarShipping />
            <SidebarDiscount />
          </div>

          <SidebarTotal />
        </>
      )}
    </div>
  );
}
