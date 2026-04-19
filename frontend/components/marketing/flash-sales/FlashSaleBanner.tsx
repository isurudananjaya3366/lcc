'use client';

import Link from 'next/link';
import { Zap, ArrowRight } from 'lucide-react';
import { CountdownTimer } from './CountdownTimer';
import type { FlashSaleListItem } from '@/types/marketing/flash-sale.types';

interface FlashSaleBannerProps {
  sale: FlashSaleListItem;
  className?: string;
}

export function FlashSaleBanner({ sale, className = '' }: FlashSaleBannerProps) {
  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-gradient-to-r from-red-600 to-orange-500 p-6 text-white ${className}`}
    >
      <div className="absolute right-0 top-0 h-full w-1/3 opacity-10">
        <Zap className="h-full w-full" />
      </div>

      <div className="relative z-10 flex flex-col items-center gap-4 md:flex-row md:justify-between">
        <div>
          <div className="mb-1 flex items-center gap-2">
            <Zap className="h-5 w-5 fill-yellow-300 text-yellow-300" />
            <span className="text-xs font-semibold uppercase tracking-wider">Flash Sale</span>
          </div>
          <h3 className="text-xl font-bold">{sale.title}</h3>
          <p className="mt-1 text-sm text-red-100">
            Up to {sale.discountRange.max}% off on {sale.totalProducts} products
          </p>
        </div>

        <div className="flex flex-col items-center gap-3">
          <CountdownTimer endDate={sale.endDate} variant="default" />
          <Link
            href={`/flash-sales/${sale.slug}`}
            className="inline-flex items-center gap-1.5 rounded-full bg-white px-4 py-2 text-sm font-semibold text-red-600 transition-colors hover:bg-red-50"
          >
            Shop Now <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
