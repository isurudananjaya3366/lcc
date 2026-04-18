'use client';

import { useStoreCheckoutStore } from '@/stores/store';

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function SidebarShipping() {
  const shippingMethod = useStoreCheckoutStore((s) => s.shippingMethod);

  const label = !shippingMethod
    ? 'Calculated at next step'
    : shippingMethod.price === 0
      ? 'Free'
      : formatLKR(shippingMethod.price);

  return (
    <div className="flex items-center justify-between py-1 text-sm">
      <span className="text-gray-600">Shipping</span>
      <span
        className={!shippingMethod ? 'text-xs text-gray-400 italic' : 'font-medium text-gray-900'}
      >
        {label}
      </span>
    </div>
  );
}
