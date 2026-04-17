import { cn } from '@/lib/utils';

interface CardBadgeProps {
  type: 'sale' | 'new' | 'out-of-stock';
  discountPercent?: number;
  className?: string;
}

const badgeStyles = {
  sale: 'bg-red-500 text-white',
  new: 'bg-green-500 text-white',
  'out-of-stock': 'bg-gray-500 text-white',
} as const;

const badgeLabels = {
  new: 'NEW',
  'out-of-stock': 'OUT OF STOCK',
} as const;

export function CardBadge({ type, discountPercent, className }: CardBadgeProps) {
  const label =
    type === 'sale' ? (discountPercent ? `-${discountPercent}% OFF` : 'SALE') : badgeLabels[type];

  return (
    <span
      className={cn(
        'absolute top-2 left-2 z-20 text-xs px-2 py-1 rounded font-semibold uppercase',
        badgeStyles[type],
        className
      )}
    >
      {label}
    </span>
  );
}
