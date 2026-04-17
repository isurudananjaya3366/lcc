'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import CartPageHeader from './CartPageHeader';
import CartItemsList from './CartItemsList';
import ContinueShoppingLink from './ContinueShoppingLink';
import EmptyCartPage from './EmptyCartPage';
import { CartSummaryBox } from '../CartSummary';

interface CartPageContainerProps {
  className?: string;
}

const CartPageContainer: FC<CartPageContainerProps> = ({ className }) => {
  const items = useStoreCartStore((s) => s.items);
  const getItemCount = useStoreCartStore((s) => s.getItemCount);

  const itemCount = getItemCount();

  if (items.length === 0) {
    return <EmptyCartPage />;
  }

  return (
    <div className={cn('mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8', className)}>
      {/* Header row */}
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <CartPageHeader itemCount={itemCount} />
        <ContinueShoppingLink />
      </div>

      {/* Two-column layout: items left, summary right */}
      <div className="flex flex-col gap-8 lg:flex-row">
        <CartItemsList className="flex-1" />

        <aside className="w-full lg:w-96 lg:flex-shrink-0 lg:sticky lg:top-24 lg:self-start">
          <CartSummaryBox />
        </aside>
      </div>
    </div>
  );
};

export default CartPageContainer;
