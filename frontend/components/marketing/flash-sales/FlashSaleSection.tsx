'use client';

import Link from 'next/link';
import { Zap, ArrowRight } from 'lucide-react';
import { useActiveFlashSales } from '@/hooks/marketing/useFlashSale';
import { FlashSaleBanner } from './FlashSaleBanner';

interface FlashSaleSectionProps {
  className?: string;
}

export function FlashSaleSection({ className = '' }: FlashSaleSectionProps) {
  const { data: sales, isLoading } = useActiveFlashSales();

  if (isLoading || !sales?.length) return null;

  return (
    <section className={`py-8 ${className}`}>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Zap className="h-6 w-6 fill-red-500 text-red-500" />
          <h2 className="text-2xl font-bold text-gray-900">Flash Sales</h2>
        </div>
        <Link
          href="/flash-sales"
          className="inline-flex items-center gap-1 text-sm font-medium text-red-600 hover:text-red-700"
        >
          View All <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      <div className="space-y-4">
        {sales.slice(0, 3).map((sale) => (
          <FlashSaleBanner key={sale.id} sale={sale} />
        ))}
      </div>
    </section>
  );
}
