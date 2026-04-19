'use client';

import Link from 'next/link';
import Image from 'next/image';
import { ShoppingCart, ZoomIn } from 'lucide-react';
import type { FlashSaleProduct, FlashSale } from '@/types/marketing/flash-sale.types';
import { DiscountBadge } from './DiscountBadge';
import { StockCounter } from './StockCounter';
import { SalePriceDisplay } from './SalePriceDisplay';
import { CountdownTimer } from './CountdownTimer';

interface FlashSaleProductCardProps {
  product: FlashSaleProduct;
  sale?: FlashSale;
  variant?: 'default' | 'compact' | 'featured';
  showTimer?: boolean;
  showStock?: boolean;
  showBadge?: boolean;
  onAddToCart?: (productId: string) => void;
  onQuickView?: (product: FlashSaleProduct) => void;
  className?: string;
}

export function FlashSaleProductCard({
  product,
  sale,
  variant = 'default',
  showTimer = false,
  showStock = true,
  showBadge = true,
  onAddToCart,
  onQuickView,
  className = '',
}: FlashSaleProductCardProps) {
  const isSoldOut = product.remainingStock <= 0;
  const isCompact = variant === 'compact';

  return (
    <div
      className={`group relative overflow-hidden rounded-xl border border-gray-200 bg-white transition-shadow hover:shadow-lg ${
        variant === 'featured' ? 'border-red-200 ring-1 ring-red-200' : ''
      } ${className}`}
    >
      {showBadge && (
        <DiscountBadge percentage={product.discountPercentage} className="absolute left-3 top-3 z-10" />
      )}

      <Link href={`/products/${product.slug}`} className="block">
        <div className={`relative overflow-hidden bg-gray-100 ${isCompact ? 'aspect-[4/3]' : 'aspect-square'}`}>
          <Image
            src={product.image}
            alt={product.name}
            fill
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
            className="object-cover transition-transform group-hover:scale-105"
          />
          {isSoldOut && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/50">
              <span className="rounded-full bg-white px-4 py-1.5 text-sm font-bold text-red-600">Sold Out</span>
            </div>
          )}
          {/* Quick view hover overlay */}
          {onQuickView && !isSoldOut && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/0 opacity-0 transition-all group-hover:bg-black/20 group-hover:opacity-100">
              <button
                type="button"
                onClick={(e) => { e.preventDefault(); onQuickView(product); }}
                className="flex items-center gap-1.5 rounded-full bg-white px-4 py-2 text-xs font-medium text-gray-800 shadow-md transition-transform hover:scale-105"
              >
                <ZoomIn className="h-3.5 w-3.5" />
                Quick View
              </button>
            </div>
          )}
        </div>
      </Link>

      <div className={`${isCompact ? 'p-2' : 'p-3'}`}>
        <Link href={`/products/${product.slug}`}>
          <h3 className={`line-clamp-2 font-medium text-gray-800 group-hover:text-blue-600 ${isCompact ? 'text-xs' : 'text-sm'}`}>
            {product.name}
          </h3>
        </Link>

        <div className="mt-2">
          <SalePriceDisplay
            originalPrice={product.originalPrice}
            salePrice={product.salePrice}
            discountPercentage={product.discountPercentage}
          />
        </div>

        {showStock && (
          <StockCounter sold={product.soldCount} total={product.totalStock} className="mt-2" />
        )}

        {showTimer && sale && (
          <CountdownTimer endDate={sale.endDate} className="mt-2" variant="compact" />
        )}

        {!isSoldOut && onAddToCart && (
          <button
            onClick={() => onAddToCart(product.productId)}
            className={`mt-3 flex w-full items-center justify-center gap-1.5 rounded-lg bg-red-600 font-medium text-white transition-colors hover:bg-red-700 ${
              isCompact ? 'py-1.5 text-xs' : 'py-2 text-sm'
            }`}
            type="button"
          >
            <ShoppingCart className={isCompact ? 'h-3.5 w-3.5' : 'h-4 w-4'} /> Add to Cart
          </button>
        )}
      </div>
    </div>
  );
}
