interface DiscountBadgeProps {
  originalPrice: number;
  salePrice: number;
}

export function DiscountBadge({ originalPrice, salePrice }: DiscountBadgeProps) {
  const percentage = Math.round(((originalPrice - salePrice) / originalPrice) * 100);

  return (
    <span className="inline-flex items-center rounded-md bg-red-100 px-2 py-0.5 text-sm font-semibold text-red-700">
      -{percentage}% OFF
    </span>
  );
}
