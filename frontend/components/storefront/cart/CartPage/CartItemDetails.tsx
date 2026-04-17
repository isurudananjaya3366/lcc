import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import CartItemVariantTags from './CartItemVariantTags';

interface CartItemDetailsProps {
  name: string;
  sku: string;
  variants: Record<string, string> | null;
  className?: string;
}

const CartItemDetails: FC<CartItemDetailsProps> = ({ name, sku, variants, className }) => {
  return (
    <div className={cn('flex flex-col gap-1 min-w-0', className)}>
      <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
        {name}
      </h3>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        SKU: {sku}
      </p>
      <CartItemVariantTags variants={variants} />
    </div>
  );
};

export default CartItemDetails;
