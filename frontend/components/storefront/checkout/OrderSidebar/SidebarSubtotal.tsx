'use client';

import { useStoreCartStore } from '@/stores/store';

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function SidebarSubtotal() {
  const subtotal = useStoreCartStore((s) => s.getSubtotal());

  return (
    <div className="flex items-center justify-between py-1 text-sm">
      <span className="text-gray-600">Subtotal</span>
      <span className="font-medium text-gray-900">{formatLKR(subtotal)}</span>
    </div>
  );
}
