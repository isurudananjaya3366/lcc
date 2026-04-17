'use client';

import { useState } from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import type { StoreProduct } from '@/types/store/product';

interface CardAddToCartProps {
  product: StoreProduct;
  className?: string;
}

export function CardAddToCart({ product, className }: CardAddToCartProps) {
  const addToCart = useStoreCartStore((s) => s.addToCart);
  const [isAdding, setIsAdding] = useState(false);
  const [isAdded, setIsAdded] = useState(false);

  const isOutOfStock = product.stockQuantity <= 0 && !product.allowBackorder;
  const hasVariants = product.variants.length > 0;

  const handleAdd = (e: React.MouseEvent) => {
    e.stopPropagation();
    e.preventDefault();
    if (isAdding || isAdded) return;

    setIsAdding(true);
    const primaryImage = product.images.find((img) => img.isPrimary) ?? product.images[0];
    addToCart(
      {
        productId: product.id,
        name: product.name,
        sku: product.sku,
        price: product.price,
        image: primaryImage?.url ?? '',
      },
      1
    );

    setTimeout(() => {
      setIsAdding(false);
      setIsAdded(true);
      setTimeout(() => setIsAdded(false), 1500);
    }, 400);
  };

  const baseClasses = 'w-full px-3 py-2 text-sm rounded-md font-medium transition-colors';

  if (isOutOfStock) {
    return (
      <div className={cn('px-3 pb-3', className)}>
        <button
          type="button"
          disabled
          className={cn(baseClasses, 'bg-gray-100 text-gray-400 cursor-not-allowed')}
        >
          Out of Stock
        </button>
      </div>
    );
  }

  if (hasVariants) {
    return (
      <div className={cn('px-3 pb-3', className)}>
        <Link
          href={`/products/${product.slug}`}
          onClick={(e) => e.stopPropagation()}
          className={cn(baseClasses, 'block text-center bg-blue-600 text-white hover:bg-blue-700')}
        >
          Select Options
        </Link>
      </div>
    );
  }

  return (
    <div className={cn('px-3 pb-3', className)}>
      <button
        type="button"
        onClick={handleAdd}
        disabled={isAdding}
        className={cn(baseClasses, 'bg-blue-600 text-white hover:bg-blue-700', {
          'opacity-75 cursor-wait': isAdding,
        })}
      >
        {isAdding ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="animate-spin h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Adding…
          </span>
        ) : isAdded ? (
          <span className="flex items-center justify-center gap-1">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Added ✓
          </span>
        ) : (
          <span className="flex items-center justify-center gap-1.5">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="9" cy="21" r="1" />
              <circle cx="20" cy="21" r="1" />
              <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
            </svg>
            Add to Cart
          </span>
        )}
      </button>
    </div>
  );
}
