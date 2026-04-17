import { DiscountBadge } from './DiscountBadge';
import { TaxInfo } from './TaxInfo';

interface PriceDisplayProps {
  price: number;
  salePrice: number | null;
  currency: string;
}

function formatPrice(amount: number, currency: string): string {
  if (currency === 'LKR') {
    return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  }
  return `${currency} ${amount.toFixed(2)}`;
}

export function PriceDisplay({ price, salePrice, currency }: PriceDisplayProps) {
  const hasDiscount = salePrice !== null && salePrice < price;
  const currentPrice = hasDiscount ? salePrice! : price;

  return (
    <div className="space-y-1">
      <div className="flex items-baseline gap-3">
        <span
          className={`text-2xl font-bold ${hasDiscount ? 'text-red-600' : 'text-gray-900'}`}
        >
          {formatPrice(currentPrice, currency)}
        </span>

        {hasDiscount && (
          <span className="text-lg text-gray-500 line-through">
            {formatPrice(price, currency)}
          </span>
        )}

        {hasDiscount && (
          <DiscountBadge originalPrice={price} salePrice={salePrice!} />
        )}
      </div>

      <TaxInfo />
    </div>
  );
}
