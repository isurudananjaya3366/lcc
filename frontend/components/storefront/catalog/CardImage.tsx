'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';
import type { StoreProduct } from '@/types/store/product';
import { StoreProductStatus } from '@/types/store/product';
import { CardBadge } from './CardBadge';
import { CardQuickActions } from './CardQuickActions';

interface CardImageProps {
  product: StoreProduct;
  onQuickView?: () => void;
  className?: string;
}

export function CardImage({ product, onQuickView, className }: CardImageProps) {
  const primaryImage = product.images.find((img) => img.isPrimary) ?? product.images[0] ?? null;
  const secondaryImage = product.images.length > 1 ? product.images[1] : null;

  const discountPercent =
    product.isOnSale && product.compareAtPrice && product.compareAtPrice > product.price
      ? Math.round(((product.compareAtPrice - product.price) / product.compareAtPrice) * 100)
      : undefined;

  const badgeType =
    product.status === StoreProductStatus.OUT_OF_STOCK
      ? 'out-of-stock'
      : product.isOnSale
        ? 'sale'
        : product.isFeatured
          ? 'new'
          : null;

  return (
    <div className={cn('relative overflow-hidden aspect-square bg-gray-100', className)}>
      {primaryImage ? (
        <Image
          src={primaryImage.url}
          alt={primaryImage.altText ?? product.name}
          fill
          className="object-cover"
          sizes="(max-width:640px) 50vw, (max-width:1024px) 33vw, 25vw"
        />
      ) : (
        <div className="absolute inset-0 bg-gray-200" />
      )}

      {secondaryImage && (
        <Image
          src={secondaryImage.url}
          alt={secondaryImage.altText ?? product.name}
          fill
          className="absolute inset-0 object-cover opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          sizes="(max-width:640px) 50vw, (max-width:1024px) 33vw, 25vw"
        />
      )}

      {badgeType && <CardBadge type={badgeType} discountPercent={discountPercent} />}

      <CardQuickActions productId={product.id} onQuickView={onQuickView} />
    </div>
  );
}
