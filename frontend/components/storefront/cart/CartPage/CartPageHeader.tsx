import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface CartPageHeaderProps {
  itemCount: number;
  className?: string;
}

const CartPageHeader: FC<CartPageHeaderProps> = ({ itemCount, className }) => {
  return (
    <h1 className={cn('text-2xl font-bold text-gray-900 dark:text-gray-100 md:text-3xl', className)}>
      Shopping Cart{' '}
      <span className="text-lg font-normal text-gray-500 dark:text-gray-400 md:text-xl">
        ({itemCount} {itemCount === 1 ? 'item' : 'items'})
      </span>
    </h1>
  );
};

export default CartPageHeader;
