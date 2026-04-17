'use client';

interface SaleBadgeOverlayProps {
  salePrice: number;
  originalPrice: number;
}

export function SaleBadgeOverlay({ salePrice, originalPrice }: SaleBadgeOverlayProps) {
  if (salePrice >= originalPrice || originalPrice <= 0) return null;

  const percentOff = Math.round(((originalPrice - salePrice) / originalPrice) * 100);

  if (percentOff <= 0) return null;

  return (
    <div className="absolute top-3 left-3 z-10">
      <span className="inline-flex items-center rounded-md bg-red-600 px-2.5 py-1 text-xs font-semibold text-white shadow-sm">
        -{percentOff}%
      </span>
    </div>
  );
}
