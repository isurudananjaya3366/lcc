'use client';

import { Zap } from 'lucide-react';
import { useFlashSales } from '@/hooks/marketing/useFlashSale';
import { FlashSaleBanner } from '@/components/marketing/flash-sales/FlashSaleBanner';

export default function FlashSalesPage() {
  const { data: sales, isLoading, error } = useFlashSales();

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="mb-8 flex items-center gap-3">
        <Zap className="h-8 w-8 fill-red-500 text-red-500" />
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Flash Sales</h1>
          <p className="text-gray-600">Limited-time deals with incredible discounts</p>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 animate-pulse rounded-xl bg-gray-200" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-center text-red-600">
          Failed to load flash sales. Please try again.
        </div>
      )}

      {sales && sales.length === 0 && (
        <div className="py-16 text-center text-gray-500">
          <Zap className="mx-auto mb-4 h-12 w-12 text-gray-300" />
          <p className="text-lg font-medium">No active flash sales</p>
          <p className="mt-1 text-sm">Check back later for amazing deals!</p>
        </div>
      )}

      {sales && sales.length > 0 && (
        <div className="space-y-6">
          {sales.map((sale) => (
            <FlashSaleBanner key={sale.id} sale={sale} />
          ))}
        </div>
      )}
    </div>
  );
}
