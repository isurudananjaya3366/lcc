'use client';

import { ProductImage } from './ProductImage';
import { PriceDisplay } from './PriceDisplay';
import { StockIndicator } from './StockIndicator';
import type { QuickButton as QBType } from '../types';

interface QuickButtonProps {
  button: QBType;
  onClick: (button: QBType) => void;
}

export function QuickButton({ button, onClick }: QuickButtonProps) {
  const isDisabled = !button.inStock;
  return (
    <button
      onClick={() => onClick(button)}
      disabled={isDisabled}
      className={`relative flex flex-col items-center gap-1 rounded-lg border p-2 text-center transition-all ${
        isDisabled
          ? 'cursor-not-allowed border-gray-200 bg-gray-50 opacity-60 dark:border-gray-700 dark:bg-gray-800'
          : 'border-gray-200 bg-white hover:border-primary hover:shadow-sm active:scale-[0.98] dark:border-gray-700 dark:bg-gray-800 dark:hover:border-primary'
      }`}
      aria-label={`Add ${button.label} to cart`}
    >
      <div className="relative">
        <ProductImage src={button.imageUrl} alt={button.label} size="md" />
        <StockIndicator quantity={button.stockQuantity} variant="overlay" />
      </div>
      <p className="line-clamp-2 w-full text-xs font-medium text-gray-800 dark:text-gray-200">
        {button.label}
      </p>
      <PriceDisplay price={button.price} size="sm" />
    </button>
  );
}
