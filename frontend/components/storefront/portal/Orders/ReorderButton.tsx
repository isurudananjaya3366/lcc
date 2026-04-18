'use client';

import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { useStoreCartStore } from '@/stores/store/cart';
import type { PortalOrderItem } from '@/types/storefront/portal.types';

interface ReorderButtonProps {
  items: PortalOrderItem[];
}

export function ReorderButton({ items }: ReorderButtonProps) {
  const router = useRouter();
  const addToCart = useStoreCartStore((s) => s.addToCart);

  const handleReorder = () => {
    for (const item of items) {
      addToCart(
        {
          productId: item.productId,
          name: item.name,
          sku: item.sku,
          price: item.price,
          image: item.image,
          variant: item.variant,
        },
        item.quantity
      );
    }

    toast.success('Items added to cart');
    router.push('/cart');
  };

  return (
    <Button variant="outline" onClick={handleReorder} className="gap-2">
      <RefreshCw className="h-4 w-4" />
      Reorder
    </Button>
  );
}
