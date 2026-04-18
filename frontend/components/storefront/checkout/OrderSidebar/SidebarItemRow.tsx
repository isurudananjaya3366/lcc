'use client';

import Image from 'next/image';

interface SidebarItemRowProps {
  name: string;
  image: string;
  price: number;
  quantity: number;
  variant: Record<string, string> | null;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export default function SidebarItemRow({
  name,
  image,
  price,
  quantity,
  variant,
}: SidebarItemRowProps) {
  return (
    <div className="flex items-center gap-3 py-2">
      {/* Image with quantity badge */}
      <div className="relative h-12 w-12 flex-shrink-0 rounded-md border bg-white">
        <Image
          src={image || '/images/placeholder.png'}
          alt={name}
          fill
          className="rounded-md object-cover"
          sizes="48px"
        />
        {quantity > 1 && (
          <span className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-gray-700 text-[10px] font-medium text-white">
            ×{quantity}
          </span>
        )}
      </div>

      {/* Name & variant */}
      <div className="flex-1 min-w-0">
        <p className="truncate text-sm font-medium text-gray-900">{name}</p>
        {variant && Object.keys(variant).length > 0 && (
          <p className="truncate text-xs text-gray-500">{Object.values(variant).join(' / ')}</p>
        )}
      </div>

      {/* Price */}
      <span className="flex-shrink-0 text-sm font-medium text-gray-900">
        {formatLKR(price * quantity)}
      </span>
    </div>
  );
}
