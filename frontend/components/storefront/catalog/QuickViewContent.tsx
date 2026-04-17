'use client';

import Image from 'next/image';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { useState } from 'react';
import { useProduct } from '@/hooks/queries/useStoreProducts';
import { useStoreCartStore } from '@/stores/store/cart';
import { CardVariantSelect } from './CardVariantSelect';

interface QuickViewContentProps {
  /** Product slug — used to fetch product details. */
  productSlug: string;
  className?: string;
}

export function QuickViewContent({ productSlug, className }: QuickViewContentProps) {
  const [quantity, setQuantity] = useState(1);
  const [selectedVariantId, setSelectedVariantId] = useState<string | null>(null);
  const { data: product, isLoading, isError } = useProduct(productSlug);
  const addToCart = useStoreCartStore((s) => s.addToCart);

  const selectedVariant = product?.variants.find((v) => v.id === selectedVariantId) ?? null;
  const effectivePrice = selectedVariant?.price ?? product?.price ?? 0;
  const comparePrice = selectedVariant?.compareAtPrice ?? product?.compareAtPrice;
  const primaryImage = product?.images.find((i) => i.isPrimary) ?? product?.images[0] ?? null;
  const isOutOfStock = (product?.stockQuantity ?? 0) <= 0 && !(product?.allowBackorder ?? false);
  const hasVariants = (product?.variants.length ?? 0) > 0;

  const handleAddToCart = () => {
    if (!product) return;
    addToCart(
      {
        productId: product.id,
        name: product.name,
        sku: selectedVariant?.sku ?? product.sku,
        price: effectivePrice,
        image: primaryImage?.url ?? '',
        variant: selectedVariant
          ? Object.fromEntries(selectedVariant.options.map((o) => [o.name, o.value]))
          : undefined,
      },
      quantity
    );
  };

  if (isLoading) {
    return (
      <div className="p-6" role="status">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="aspect-square bg-gray-200 animate-pulse rounded-lg" />
          <div className="space-y-4">
            <div className="h-6 w-3/4 bg-gray-200 animate-pulse rounded" />
            <div className="h-5 w-1/4 bg-gray-200 animate-pulse rounded" />
            <div className="h-20 bg-gray-200 animate-pulse rounded" />
            <div className="h-10 w-full bg-gray-200 animate-pulse rounded" />
          </div>
        </div>
        <span className="sr-only">Loading product details...</span>
      </div>
    );
  }

  if (isError || !product) {
    return (
      <div className="p-6 text-center text-gray-500">
        <p className="text-sm">Failed to load product details. Please try again.</p>
        <Link
          href={`/products/${productSlug}`}
          className="mt-4 inline-block text-sm font-medium text-blue-600 hover:underline"
        >
          View full product page →
        </Link>
      </div>
    );
  }

  return (
    <div className={cn('p-6', className)}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left — Image */}
        <div className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden">
          {primaryImage ? (
            <Image
              src={primaryImage.url}
              alt={primaryImage.altText ?? product.name}
              fill
              className="object-cover"
              sizes="(max-width:768px) 100vw, 400px"
              priority
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <svg
                width="64"
                height="64"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#D1D5DB"
                strokeWidth="1.5"
                aria-hidden="true"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <path d="m21 15-5-5L5 21" />
              </svg>
            </div>
          )}
        </div>

        {/* Right — Details */}
        <div className="flex flex-col">
          {/* Category */}
          {product.categoryName && (
            <Link
              href={`/products/category/${product.categorySlug}`}
              className="text-xs font-medium text-blue-600 hover:underline mb-1"
            >
              {product.categoryName}
            </Link>
          )}

          {/* Title */}
          <h2 className="text-xl font-semibold text-gray-900">{product.name}</h2>

          {/* Price */}
          <div className="mt-2 flex items-baseline gap-2 flex-wrap">
            <span className="text-lg font-bold text-gray-900">
              ₨ {effectivePrice.toLocaleString()}
            </span>
            {comparePrice && comparePrice > effectivePrice && (
              <span className="text-sm text-gray-400 line-through">
                ₨ {comparePrice.toLocaleString()}
              </span>
            )}
          </div>

          {/* Stock status */}
          <p
            className={cn(
              'mt-1.5 text-sm font-medium',
              isOutOfStock ? 'text-red-600' : 'text-green-600'
            )}
          >
            {isOutOfStock ? 'Out of Stock' : 'In Stock'}
          </p>

          {/* Short description */}
          {(product.shortDescription ?? product.description) && (
            <p className="mt-3 text-sm text-gray-600 line-clamp-3">
              {product.shortDescription ?? product.description}
            </p>
          )}

          {/* Variant selector */}
          {hasVariants && (
            <div className="mt-3">
              <p className="text-sm font-medium text-gray-700 mb-1.5">Options</p>
              <CardVariantSelect
                variants={product.variants}
                selectedVariantId={selectedVariantId}
                onVariantChange={setSelectedVariantId}
              />
            </div>
          )}

          {/* Quantity */}
          <div className="mt-4">
            <label className="text-sm font-medium text-gray-700">Quantity</label>
            <div className="mt-1.5 flex items-center">
              <button
                type="button"
                onClick={() => setQuantity((q) => Math.max(1, q - 1))}
                disabled={quantity <= 1}
                className="w-9 h-9 flex items-center justify-center rounded-l-md border border-gray-300 bg-gray-50 text-gray-600 hover:bg-gray-100 disabled:opacity-40 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                aria-label="Decrease quantity"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  aria-hidden="true"
                >
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </button>
              <span className="w-12 h-9 flex items-center justify-center border-y border-gray-300 text-sm font-medium text-gray-900">
                {quantity}
              </span>
              <button
                type="button"
                onClick={() => setQuantity((q) => q + 1)}
                className="w-9 h-9 flex items-center justify-center rounded-r-md border border-gray-300 bg-gray-50 text-gray-600 hover:bg-gray-100 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                aria-label="Increase quantity"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  aria-hidden="true"
                >
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Add to Cart */}
          <button
            type="button"
            disabled={isOutOfStock}
            onClick={handleAddToCart}
            className="mt-6 w-full rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
          >
            {isOutOfStock ? 'Out of Stock' : 'Add to Cart'}
          </button>

          {/* View full page link */}
          <Link
            href={`/products/${product.slug}`}
            className="mt-3 text-center text-sm text-blue-600 hover:underline"
          >
            View full product details →
          </Link>
        </div>
      </div>
    </div>
  );
}
