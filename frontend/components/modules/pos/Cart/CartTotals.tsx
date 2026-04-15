'use client';

import { useCartStore } from '@/stores/pos/cart';
import { calculateCartTotals } from '@/lib/pos/calculateTax';
import { SubtotalDisplay } from './SubtotalDisplay';
import { DiscountSection } from './DiscountSection';
import { TaxDisplay } from './TaxDisplay';
import { GrandTotalDisplay } from './GrandTotalDisplay';
import { ItemsCountDisplay } from './ItemsCountDisplay';

export function CartTotals() {
  const { getSubtotal, getDiscountTotal, getItemCount } = useCartStore();

  const subtotal = getSubtotal();
  const discountTotal = getDiscountTotal();
  const totals = calculateCartTotals(subtotal, discountTotal);

  return (
    <div className="space-y-1.5 text-sm">
      <ItemsCountDisplay count={getItemCount()} />
      <SubtotalDisplay amount={totals.subtotal} />
      <DiscountSection amount={totals.discountAmount} subtotal={subtotal} />
      <TaxDisplay amount={totals.taxAmount} rate={totals.taxRate} name={totals.taxName} />
      <div className="border-t border-gray-300 pt-1.5 dark:border-gray-600">
        <GrandTotalDisplay amount={totals.grandTotal} />
      </div>
    </div>
  );
}
