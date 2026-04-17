'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import type { Product } from '@/lib/api/store/modules/products';
import { formatCurrency } from '@/lib/store/config';
import Link from 'next/link';
import Image from 'next/image';

interface PopularProductsFallbackProps {
  className?: string;
}

const API_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

export function PopularProductsFallback({ className }: PopularProductsFallbackProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchFeatured() {
      try {
        const res = await fetch(
          `${API_URL}/products/?featured=true&page_size=4`,
          { signal: controller.signal },
        );
        if (!res.ok) throw new Error('Failed to fetch');
        const data = await res.json();
        setProducts(data.results ?? data);
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          setProducts([]);
        }
      } finally {
        setIsLoading(false);
      }
    }

    fetchFeatured();
    return () => controller.abort();
  }, []);

  if (isLoading) {
    return (
      <div className={cn('space-y-3', className)} aria-busy="true">
        <h3 className="text-sm font-semibold text-foreground">Popular Products</h3>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }, (_, i) => (
            <div
              key={i}
              className="h-48 animate-pulse rounded-lg bg-muted"
            />
          ))}
        </div>
      </div>
    );
  }

  if (products.length === 0) return null;

  return (
    <div className={cn('space-y-3', className)}>
      <h3 className="text-sm font-semibold text-foreground">Popular Products</h3>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {products.map((product) => (
          <Link
            key={product.id}
            href={`/store/product/${product.slug}`}
            className="group rounded-lg border border-border bg-background p-3 transition-shadow hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <div className="relative mb-2 aspect-square overflow-hidden rounded-md bg-muted">
              {product.images[0] && (
                <Image
                  src={product.images[0].url}
                  alt={product.images[0].alt_text || product.name}
                  fill
                  className="object-cover transition-transform group-hover:scale-105"
                  sizes="(max-width: 640px) 50vw, 25vw"
                />
              )}
            </div>
            <p className="truncate text-sm font-medium text-foreground">
              {product.name}
            </p>
            <p className="text-sm text-muted-foreground">
              {formatCurrency(product.sale_price ?? product.price)}
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
