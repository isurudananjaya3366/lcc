import { cn } from '@/lib/utils';

interface CardPriceProps {
  price: number;
  compareAtPrice?: number;
  currency?: string;
  className?: string;
}

export function CardPrice({ price, compareAtPrice, currency = '₨', className }: CardPriceProps) {
  if (price === 0) {
    return (
      <div className={cn('flex items-center gap-2 flex-wrap', className)}>
        <span className="text-base font-bold text-green-600">Free</span>
      </div>
    );
  }

  const isOnSale = compareAtPrice != null && compareAtPrice > price;

  if (isOnSale) {
    const percent = Math.round(((compareAtPrice - price) / compareAtPrice) * 100);
    return (
      <div className={cn('flex items-center gap-2 flex-wrap', className)}>
        <span className="text-base font-bold text-red-600">
          {currency} {price.toLocaleString()}
        </span>
        <span className="text-xs text-gray-400 line-through">
          {currency} {compareAtPrice.toLocaleString()}
        </span>
        <span className="text-xs font-semibold text-white bg-red-500 px-1.5 py-0.5 rounded">
          -{percent}%
        </span>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-2 flex-wrap', className)}>
      <span className="text-base font-bold text-gray-900">
        {currency} {price.toLocaleString()}
      </span>
    </div>
  );
}
