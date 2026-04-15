'use client';

import { ShoppingCart } from 'lucide-react';

export function EmptyCart() {
  return (
    <div className="flex h-full flex-col items-center justify-center text-gray-400 dark:text-gray-500">
      <ShoppingCart className="h-16 w-16 opacity-40" />
      <p className="mt-3 text-sm font-medium">Cart is empty</p>
      <p className="mt-1 text-xs">Search or scan products to add items</p>
      <p className="mt-2 text-[10px] text-gray-300 dark:text-gray-600">
        Press F2 to focus search
      </p>
    </div>
  );
}
