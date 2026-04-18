'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, ShoppingBag } from 'lucide-react';
import { useStoreCartStore } from '@/stores/store';
import OrderSidebar from './OrderSidebar';

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function CollapsibleSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const total = useStoreCartStore((s) => s.getTotal());
  const itemCount = useStoreCartStore((s) => s.getItemCount());

  return (
    <div className="lg:hidden">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="flex w-full items-center justify-between rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-sm shadow-sm transition-colors hover:bg-gray-100"
        aria-expanded={isOpen}
        aria-controls="mobile-order-sidebar"
      >
        <span className="flex items-center gap-2 font-medium text-gray-900">
          <ShoppingBag className="h-4 w-4" />
          Order Summary
          {itemCount > 0 && (
            <span className="inline-flex h-5 min-w-[20px] items-center justify-center rounded-full bg-gray-800 px-1.5 text-[10px] font-medium text-white">
              {itemCount}
            </span>
          )}
          <span className="text-gray-400">·</span>
          <span>{formatLKR(total)}</span>
        </span>
        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-gray-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-gray-500" />
        )}
      </button>

      {isOpen && (
        <div id="mobile-order-sidebar" className="mt-3">
          <OrderSidebar />
        </div>
      )}
    </div>
  );
}
