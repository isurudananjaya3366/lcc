'use client';

import Image from 'next/image';
import { useStoreCartStore, type StoreCartItem } from '@/stores/store';

const OrderItemRow = ({ item }: { item: StoreCartItem }) => {
  const variantLabel = item.variant ? Object.values(item.variant).join(' / ') : null;

  return (
    <div className="flex items-center gap-4 py-3">
      <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-md border bg-gray-50">
        <Image
          src={item.image || '/placeholder.png'}
          alt={item.name}
          fill
          className="object-cover"
          sizes="56px"
        />
        <span className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-gray-700 text-[10px] font-medium text-white">
          {item.quantity}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
        {variantLabel && <p className="text-xs text-gray-500">{variantLabel}</p>}
      </div>
      <p className="shrink-0 text-sm font-medium text-gray-900">
        ₨{item.lineSubtotal.toLocaleString()}
      </p>
    </div>
  );
};

export const OrderItemsReview = () => {
  const items = useStoreCartStore((s) => s.items);

  return (
    <div className="divide-y divide-gray-100">
      {items.map((item) => (
        <OrderItemRow key={item.id} item={item} />
      ))}
    </div>
  );
};
