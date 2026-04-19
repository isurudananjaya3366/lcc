import { Zap } from 'lucide-react';

interface SalePriceDisplayProps {
  originalPrice: number;
  salePrice: number;
  discountPercentage: number;
  className?: string;
}

export function SalePriceDisplay({ originalPrice, salePrice, discountPercentage, className = '' }: SalePriceDisplayProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-2xl font-bold text-red-600">₨{salePrice.toLocaleString()}</span>
      <span className="text-sm text-gray-400 line-through">₨{originalPrice.toLocaleString()}</span>
      <span className="inline-flex items-center gap-0.5 rounded bg-red-100 px-1.5 py-0.5 text-xs font-semibold text-red-600">
        <Zap className="h-3 w-3" />
        {discountPercentage}% OFF
      </span>
    </div>
  );
}
