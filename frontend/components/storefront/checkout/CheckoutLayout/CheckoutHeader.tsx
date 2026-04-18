'use client';

import Link from 'next/link';
import { Lock, ShoppingBag } from 'lucide-react';
import { useStoreCartStore } from '@/stores/store';

export const CheckoutHeader = () => {
  const itemCount = useStoreCartStore((s) => s.getItemCount());

  return (
    <header className="border-b bg-white">
      <div className="container mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-xl font-bold text-gray-900">
          LankaCom
        </Link>

        <div className="flex items-center gap-2 text-sm text-gray-600">
          <Lock className="h-4 w-4" />
          <span className="hidden sm:inline">Secure Checkout</span>
        </div>

        <Link
          href="/cart"
          className="relative flex items-center gap-1 text-gray-600 hover:text-gray-900 transition-colors"
        >
          <ShoppingBag className="h-5 w-5" />
          {itemCount > 0 && (
            <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs font-medium text-white">
              {itemCount}
            </span>
          )}
        </Link>
      </div>
    </header>
  );
};
