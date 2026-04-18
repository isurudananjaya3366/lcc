'use client';

import Image from 'next/image';
import Link from 'next/link';
import type { PortalOrderItem } from '@/types/storefront/portal.types';

interface OrderItemRowProps {
  item: PortalOrderItem;
}

const formatLKR = (amount: number) =>
  `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;

export function OrderItemRow({ item }: OrderItemRowProps) {
  return (
    <div className="flex gap-4 py-4">
      <Link
        href={`/products/${item.productId}`}
        className="relative h-16 w-16 shrink-0 overflow-hidden rounded-md border bg-muted"
      >
        <Image
          src={item.image}
          alt={item.name}
          fill
          className="object-cover"
          sizes="64px"
        />
      </Link>

      <div className="flex flex-1 flex-col justify-between sm:flex-row sm:items-center">
        <div className="space-y-0.5">
          <Link
            href={`/products/${item.productId}`}
            className="font-medium hover:underline"
          >
            {item.name}
          </Link>
          <p className="text-xs text-muted-foreground">SKU: {item.sku}</p>
          {item.variant && Object.keys(item.variant).length > 0 && (
            <p className="text-xs text-muted-foreground">
              {Object.entries(item.variant)
                .map(([key, value]) => `${key}: ${value}`)
                .join(', ')}
            </p>
          )}
        </div>

        <div className="mt-1 flex items-center gap-4 sm:mt-0 sm:text-right">
          <span className="text-sm text-muted-foreground">
            {item.quantity} × {formatLKR(item.price)}
          </span>
          <span className="font-medium">{formatLKR(item.lineTotal)}</span>
        </div>
      </div>
    </div>
  );
}
