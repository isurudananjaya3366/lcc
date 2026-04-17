'use client';

import Link from 'next/link';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import type { StoreProduct } from '@/types/store/product';
import { CardImage } from './CardImage';
import { CardContent } from './CardContent';
import { CardAddToCart } from './CardAddToCart';
import { QuickViewModal } from './QuickViewModal';

interface ProductCardProps {
  product: StoreProduct;
  className?: string;
}

export function ProductCard({ product, className }: ProductCardProps) {
  const [quickViewOpen, setQuickViewOpen] = useState(false);

  return (
    <>
      <article
        className={cn(
          'group border rounded-lg shadow-sm hover:shadow-md transition-shadow bg-white overflow-hidden',
          className
        )}
      >
        <Link href={`/products/${product.slug}`}>
          <CardImage product={product} onQuickView={() => setQuickViewOpen(true)} />
        </Link>
        <CardContent product={product} />
        <CardAddToCart product={product} />
      </article>

      <QuickViewModal
        isOpen={quickViewOpen}
        onClose={() => setQuickViewOpen(false)}
        productSlug={product.slug}
      />
    </>
  );
}
