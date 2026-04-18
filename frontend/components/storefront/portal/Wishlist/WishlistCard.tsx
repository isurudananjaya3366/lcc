'use client';

import Link from 'next/link';
import Image from 'next/image';
import { ShoppingCart, Trash2 } from 'lucide-react';
import type { WishlistItem } from '@/types/storefront/portal.types';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface WishlistCardProps {
  item: WishlistItem;
  onRemove: (id: string) => void;
  onAddToCart: (item: WishlistItem) => void;
}

export function WishlistCard({ item, onRemove, onAddToCart }: WishlistCardProps) {
  return (
    <Card className="overflow-hidden">
      <Link href={`/products/${item.slug}`} className="block">
        <div className="relative aspect-square bg-muted">
          <Image
            src={item.image}
            alt={item.name}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw"
          />
        </div>
      </Link>
      <CardContent className="p-3 space-y-2">
        <Link href={`/products/${item.slug}`} className="hover:underline">
          <h3 className="font-medium text-sm line-clamp-2">{item.name}</h3>
        </Link>
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm">
            ₨ {item.price.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
          </span>
          {item.compareAtPrice && (
            <span className="text-xs text-muted-foreground line-through">
              ₨ {item.compareAtPrice.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </span>
          )}
        </div>
        <Badge variant={item.inStock ? 'default' : 'destructive'} className="text-xs">
          {item.inStock ? 'In Stock' : 'Out of Stock'}
        </Badge>
        <div className="flex gap-2 pt-1">
          <Button
            size="sm"
            className="flex-1 text-xs"
            disabled={!item.inStock}
            onClick={() => onAddToCart(item)}
          >
            <ShoppingCart className="h-3.5 w-3.5 mr-1" />
            Add to Cart
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onRemove(item.id)}>
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          Added {new Date(item.addedAt).toLocaleDateString()}
        </p>
      </CardContent>
    </Card>
  );
}
