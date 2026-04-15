interface PriceDisplayProps {
  price: number | null | undefined;
  originalPrice?: number;
  size?: 'sm' | 'md' | 'lg';
  showFrom?: boolean;
}

const sizeClasses = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
} as const;

function formatLKR(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function PriceDisplay({
  price,
  originalPrice,
  size = 'md',
  showFrom = false,
}: PriceDisplayProps) {
  if (price === null || price === undefined) {
    return <span className={`${sizeClasses[size]} text-gray-400 italic`}>Price unavailable</span>;
  }

  if (price === 0) {
    return <span className={`${sizeClasses[size]} text-gray-400 italic`}>Contact for price</span>;
  }

  const hasDiscount = originalPrice !== undefined && originalPrice > price;

  return (
    <div className="flex flex-col items-end">
      {hasDiscount && (
        <span className="text-xs text-gray-400 line-through">{formatLKR(originalPrice)}</span>
      )}
      <span className={`${sizeClasses[size]} font-semibold text-gray-900 dark:text-gray-100`}>
        {showFrom && 'From '}
        {formatLKR(price)}
      </span>
    </div>
  );
}
