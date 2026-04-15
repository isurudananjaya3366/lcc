'use client';

import { memo, useState } from 'react';
import { ItemName } from './ItemName';
import { QuantityControls } from './QuantityControls';
import { ItemPrice } from './ItemPrice';
import { RemoveItemButton } from './RemoveItemButton';
import { ItemOptionsMenu } from './ItemOptionsMenu';
import { ItemDiscount } from './ItemDiscount';
import { useCartStore } from '@/stores/pos/cart';
import type { POSCartItem } from '../types';

interface CartItemProps {
  item: POSCartItem;
}

export const CartItem = memo(function CartItem({ item }: CartItemProps) {
  const { updateQuantity, removeItem, applyItemDiscount, removeItemDiscount } = useCartStore();
  const [showDiscount, setShowDiscount] = useState(false);

  return (
    <div className="group px-4 py-2.5 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/30">
      <div className="flex items-start gap-2">
        {/* Name + Variant */}
        <div className="min-w-0 flex-1">
          <ItemName name={item.productName} variant={item.variantName} sku={item.sku} />
        </div>

        {/* Quantity Controls */}
        <QuantityControls
          quantity={item.quantity}
          onChange={(qty) => updateQuantity(item.id, qty)}
        />

        {/* Line Price */}
        <ItemPrice
          lineTotal={item.lineTotal}
          unitPrice={item.unitPrice}
          quantity={item.quantity}
          discountAmount={item.discountAmount}
        />

        {/* Actions */}
        <div className="flex shrink-0 items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
          <ItemOptionsMenu
            hasDiscount={!!item.discount}
            onApplyDiscount={() => setShowDiscount(true)}
            onRemoveDiscount={() => removeItemDiscount(item.id)}
          />
          <RemoveItemButton onRemove={() => removeItem(item.id)} />
        </div>
      </div>

      {/* Inline Discount */}
      {showDiscount && (
        <ItemDiscount
          currentDiscount={item.discount}
          unitPrice={item.unitPrice}
          quantity={item.quantity}
          onApply={(discount) => {
            applyItemDiscount(item.id, discount);
            setShowDiscount(false);
          }}
          onCancel={() => setShowDiscount(false)}
        />
      )}
    </div>
  );
});
