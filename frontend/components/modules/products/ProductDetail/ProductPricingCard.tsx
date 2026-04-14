'use client';

import type { Product } from '@/types/product';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface ProductPricingCardProps {
  product: Product;
}

function formatLKR(value: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(value);
}

export function ProductPricingCard({ product }: ProductPricingCardProps) {
  const { pricing } = product;
  const profit = pricing.basePrice - pricing.cost;
  const margin = pricing.cost > 0 ? (profit / pricing.cost) * 100 : 0;

  const getMarginColor = () => {
    if (margin > 0) return 'text-green-600 dark:text-green-400';
    if (margin < 0) return 'text-red-600 dark:text-red-400';
    return 'text-gray-500 dark:text-gray-400';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pricing Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex justify-between">
          <span className="text-sm text-gray-500 dark:text-gray-400">Cost Price</span>
          <span className="text-sm font-medium tabular-nums">{formatLKR(pricing.cost)}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-500 dark:text-gray-400">Selling Price</span>
          <span className="text-sm font-medium tabular-nums">{formatLKR(pricing.basePrice)}</span>
        </div>
        {pricing.compareAtPrice && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">Compare at Price</span>
            <span className="text-sm tabular-nums line-through text-gray-400">
              {formatLKR(pricing.compareAtPrice)}
            </span>
          </div>
        )}
        <div className="border-t pt-3 dark:border-gray-700">
          <div className="flex justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">Profit Margin</span>
            <span className={`text-sm font-medium tabular-nums ${getMarginColor()}`}>
              {margin.toFixed(1)}%
            </span>
          </div>
        </div>
        {pricing.taxRate > 0 && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-500 dark:text-gray-400">Tax Rate</span>
            <span className="text-sm tabular-nums">{pricing.taxRate}%</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
