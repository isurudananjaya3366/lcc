'use client';

import { useStoreCartStore, type StoreCartItem } from '@/stores/store';
import SidebarItemRow from './SidebarItemRow';

interface SidebarItemsListProps {
  isLoading?: boolean;
}

export default function SidebarItemsList({ isLoading }: SidebarItemsListProps) {
  const items = useStoreCartStore((s) => s.items);

  if (isLoading) {
    return (
      <div className="space-y-3 py-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex items-center gap-3 animate-pulse">
            <div className="h-12 w-12 rounded-md bg-gray-200" />
            <div className="flex-1 space-y-1.5">
              <div className="h-3.5 w-3/4 rounded bg-gray-200" />
              <div className="h-3 w-1/2 rounded bg-gray-200" />
            </div>
            <div className="h-3.5 w-14 rounded bg-gray-200" />
          </div>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return <p className="py-6 text-center text-sm text-gray-500">Your cart is empty</p>;
  }

  return (
    <div className="max-h-64 overflow-y-auto divide-y divide-gray-100">
      {items.map((item: StoreCartItem) => (
        <SidebarItemRow
          key={item.id}
          name={item.name}
          image={item.image}
          price={item.price}
          quantity={item.quantity}
          variant={item.variant}
        />
      ))}
    </div>
  );
}
