'use client';

import Link from 'next/link';
import { Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function EmptyWishlist() {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <Heart className="h-16 w-16 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold mb-2">Your wishlist is empty</h3>
      <p className="text-muted-foreground mb-6">
        Save items you love to find them later
      </p>
      <Button asChild>
        <Link href="/products">Browse Products</Link>
      </Button>
    </div>
  );
}
