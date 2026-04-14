'use client';

interface PriceCellProps {
  price: number | null | undefined;
  currency?: string;
}

const formatter = new Intl.NumberFormat('en-LK', {
  style: 'currency',
  currency: 'LKR',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export function PriceCell({ price }: PriceCellProps) {
  if (price == null) {
    return <span className="text-gray-400">—</span>;
  }

  return (
    <span className="whitespace-nowrap text-right font-medium tabular-nums text-gray-900 dark:text-gray-100">
      {formatter.format(price)}
    </span>
  );
}
