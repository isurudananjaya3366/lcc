'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

interface RecentProduct {
  slug: string;
  name: string;
  price: number;
  currency: string;
  image: string;
}

const STORAGE_KEY = 'lcc-recently-viewed';
const MAX_ITEMS = 10;

export function addToRecentlyViewed(product: RecentProduct) {
  if (typeof window === 'undefined') return;
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') as RecentProduct[];
    const filtered = stored.filter((p) => p.slug !== product.slug);
    filtered.unshift(product);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered.slice(0, MAX_ITEMS)));
  } catch {
    // Ignore localStorage errors
  }
}

export function getRecentlyViewed(): RecentProduct[] {
  if (typeof window === 'undefined') return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') as RecentProduct[];
  } catch {
    return [];
  }
}

interface RecentlyViewedProps {
  currentSlug: string;
}

export function RecentlyViewed({ currentSlug }: RecentlyViewedProps) {
  const [products, setProducts] = useState<RecentProduct[]>([]);

  useEffect(() => {
    const all = getRecentlyViewed();
    setProducts(all.filter((p) => p.slug !== currentSlug).slice(0, 6));
  }, [currentSlug]);

  if (products.length === 0) return null;

  return (
    <section aria-label="Recently viewed products">
      <h2 className="mb-4 text-lg font-bold text-gray-900">Recently Viewed</h2>
      <div className="flex gap-4 overflow-x-auto pb-2">
        {products.map((product) => (
          <Link
            key={product.slug}
            href={`/products/${product.slug}`}
            className="flex-shrink-0 w-32 group"
          >
            <div className="relative aspect-square overflow-hidden rounded-md bg-gray-100">
              {product.image ? (
                <Image
                  src={product.image}
                  alt={product.name}
                  fill
                  sizes="128px"
                  className="object-cover"
                />
              ) : (
                <div className="flex h-full items-center justify-center text-gray-400">
                  <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" strokeWidth={1} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0 0 22.5 18.75V5.25A2.25 2.25 0 0 0 20.25 3H3.75A2.25 2.25 0 0 0 1.5 5.25v13.5A2.25 2.25 0 0 0 3.75 21Z" />
                  </svg>
                </div>
              )}
            </div>
            <p className="mt-1 text-xs font-medium text-gray-700 line-clamp-2 group-hover:text-blue-600">
              {product.name}
            </p>
            <p className="text-xs text-gray-500">
              {product.currency} {product.price.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
