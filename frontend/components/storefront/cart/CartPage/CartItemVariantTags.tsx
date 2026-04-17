import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface CartItemVariantTagsProps {
  variants: Record<string, string> | null;
  className?: string;
}

const CartItemVariantTags: FC<CartItemVariantTagsProps> = ({ variants, className }) => {
  if (!variants || Object.keys(variants).length === 0) {
    return null;
  }

  return (
    <div className={cn('flex flex-wrap gap-1.5', className)}>
      {Object.entries(variants).map(([key, value]) => (
        <span
          key={key}
          className="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 dark:bg-gray-700 dark:text-gray-300"
        >
          {key}: {value}
        </span>
      ))}
    </div>
  );
};

export default CartItemVariantTags;
