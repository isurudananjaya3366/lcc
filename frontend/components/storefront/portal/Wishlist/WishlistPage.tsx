'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import type { WishlistItem } from '@/types/storefront/portal.types';
import { getWishlist, removeFromWishlist } from '@/services/storefront/portalService';
import { useStoreCartStore } from '@/stores/store/cart';
import { WishlistGrid } from './WishlistGrid';
import { EmptyWishlist } from './EmptyWishlist';
import { WishlistHeader } from './WishlistHeader';
import { Loader2 } from 'lucide-react';

export function WishlistPage() {
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const addToCart = useStoreCartStore((s) => s.addToCart);

  useEffect(() => {
    getWishlist()
      .then(setItems)
      .catch(() => toast.error('Failed to load wishlist'))
      .finally(() => setLoading(false));
  }, []);

  const handleRemove = async (id: string) => {
    try {
      await removeFromWishlist(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      toast.success('Item removed from wishlist');
    } catch {
      toast.error('Failed to remove item');
    }
  };

  const handleAddToCart = (item: WishlistItem) => {
    addToCart({
      productId: item.productId,
      name: item.name,
      sku: item.productId,
      price: item.price,
      image: item.image,
      variant: undefined,
    });
    toast.success(`${item.name} added to cart`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <WishlistHeader count={items.length} />
      {items.length > 0 ? (
        <WishlistGrid items={items} onRemove={handleRemove} onAddToCart={handleAddToCart} />
      ) : (
        <EmptyWishlist />
      )}
    </div>
  );
}
