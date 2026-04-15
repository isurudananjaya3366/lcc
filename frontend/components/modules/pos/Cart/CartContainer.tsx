'use client';

import { ShoppingCart } from 'lucide-react';
import { CartItemsList } from './CartItemsList';
import { EmptyCart } from './EmptyCart';
import { CartTotals } from './CartTotals';
import { ClearCartDialog } from './ClearCartDialog';
import { useCartStore } from '@/stores/pos/cart';

export function CartContainer() {
  const { items, getItemCount, clearCart } = useCartStore();

  const itemCount = getItemCount();
  const isEmpty = items.length === 0;

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex shrink-0 items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <ShoppingCart className="h-4 w-4 text-gray-500" />
          <h2 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Cart</h2>
          {itemCount > 0 && (
            <span className="rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground">
              {itemCount}
            </span>
          )}
        </div>
        {!isEmpty && <ClearCartDialog onConfirm={clearCart} />}
      </div>

      {/* Items */}
      <div className="flex-1 overflow-y-auto">
        {isEmpty ? <EmptyCart /> : <CartItemsList items={items} />}
      </div>

      {/* Totals */}
      {!isEmpty && (
        <div className="shrink-0 border-t border-gray-200 bg-gray-50 px-4 py-3 dark:border-gray-700 dark:bg-gray-800/50">
          <CartTotals />
        </div>
      )}
    </div>
  );
}
