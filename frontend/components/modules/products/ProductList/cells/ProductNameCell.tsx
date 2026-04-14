'use client';

import Image from 'next/image';
import Link from 'next/link';
import type { Product } from '@/types/product';

interface ProductNameCellProps {
  product: Product;
  showSku?: boolean;
}

export function ProductNameCell({ product, showSku = true }: ProductNameCellProps) {
  const thumbnailUrl =
    product.images?.find((img) => img.isPrimary)?.thumbnailUrl ?? product.images?.[0]?.thumbnailUrl;

  return (
    <div className="flex items-center gap-3">
      <div className="h-10 w-10 flex-shrink-0 overflow-hidden rounded-md bg-gray-100 dark:bg-gray-800">
        {thumbnailUrl ? (
          <Image
            src={thumbnailUrl}
            alt={product.name}
            width={40}
            height={40}
            className="h-10 w-10 object-cover"
          />
        ) : (
          <div className="flex h-10 w-10 items-center justify-center text-gray-400">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
      </div>
      <div className="min-w-0">
        <Link
          href={`/products/${product.id}`}
          className="truncate font-medium text-gray-900 hover:text-blue-600 dark:text-gray-100 dark:hover:text-blue-400"
        >
          {product.name}
        </Link>
        {showSku && (
          <p className="truncate text-sm text-gray-500 dark:text-gray-400">{product.sku}</p>
        )}
      </div>
    </div>
  );
}
