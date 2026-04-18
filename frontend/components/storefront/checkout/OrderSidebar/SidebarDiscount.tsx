'use client';

import { useStoreCartStore } from '@/stores/store';

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function SidebarDiscount() {
  const discount = useStoreCartStore((s) => s.discount);
  const discountAmount = useStoreCartStore((s) => s.getDiscount());

  if (!discount || discountAmount === 0) return null;

  return (
    <div className="flex items-center justify-between py-1 text-sm">
      <span className="text-gray-600">
        Discount <span className="text-xs text-gray-400">({discount.code})</span>
      </span>
      <span className="font-medium text-green-600">−{formatLKR(discountAmount)}</span>
    </div>
  );
}
