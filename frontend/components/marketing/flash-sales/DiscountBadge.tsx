interface DiscountBadgeProps {
  percentage: number;
  className?: string;
}

export function DiscountBadge({ percentage, className = '' }: DiscountBadgeProps) {
  return (
    <span className={`inline-flex items-center rounded-full bg-red-600 px-2.5 py-1 text-xs font-bold text-white shadow-sm ${className}`}>
      -{percentage}%
    </span>
  );
}
