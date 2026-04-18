'use client';

import type { WishlistItem } from '@/types/storefront/portal.types';
import { WishlistCard } from './WishlistCard';

interface WishlistGridProps {
  items: WishlistItem[];
  onRemove: (id: string) => void;
  onAddToCart: (item: WishlistItem) => void;
}

export function WishlistGrid({ items, onRemove, onAddToCart }: WishlistGridProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
      {items.map((item) => (
        <WishlistCard key={item.id} item={item} onRemove={onRemove} onAddToCart={onAddToCart} />
      ))}
    </div>
  );
}
