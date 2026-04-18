'use client';

import { useStoreCartStore, useStoreCheckoutStore } from '@/stores/store';
import { COD_FEE } from '../Payment';

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function SidebarTotal() {
  const total = useStoreCartStore((s) => s.getTotal());
  const tax = useStoreCartStore((s) => s.getTax());
  const paymentMethod = useStoreCheckoutStore((s) => s.paymentMethod);

  const codFee = paymentMethod === 'cod' ? COD_FEE : 0;
  const grandTotal = total + codFee;

  return (
    <div className="border-t border-gray-200 pt-3 mt-1">
      <div className="flex items-center justify-between">
        <span className="text-base font-semibold text-gray-900">Total</span>
        <span className="text-lg font-bold text-gray-900">{formatLKR(grandTotal)}</span>
      </div>
      <div className="mt-0.5 flex items-center justify-between text-xs text-gray-500">
        <span>Including ₨{tax.toLocaleString('en-LK', { minimumFractionDigits: 2 })} tax</span>
        {codFee > 0 && <span>+ ₨{COD_FEE} COD fee</span>}
      </div>
    </div>
  );
}
