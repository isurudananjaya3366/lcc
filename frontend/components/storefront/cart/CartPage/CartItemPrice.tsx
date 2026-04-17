import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import { formatCurrency } from '@/lib/store/config';

interface CartItemPriceProps {
  price: number;
  quantity: number;
  lineSubtotal: number;
  className?: string;
}

const CartItemPrice: FC<CartItemPriceProps> = ({ price, quantity, lineSubtotal, className }) => {
  return (
    <div className={cn('flex flex-col items-end text-right', className)}>
      <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
        {formatCurrency(lineSubtotal)}
      </span>
      {quantity > 1 && (
        <span className="text-xs text-gray-500 dark:text-gray-400">
          {formatCurrency(price)} × {quantity}
        </span>
      )}
    </div>
  );
};

export default CartItemPrice;
