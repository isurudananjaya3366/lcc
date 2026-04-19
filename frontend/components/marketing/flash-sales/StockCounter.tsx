interface StockCounterProps {
  sold: number;
  total: number;
  className?: string;
}

export function StockCounter({ sold, total, className = '' }: StockCounterProps) {
  const percentage = total > 0 ? Math.min(100, Math.round((sold / total) * 100)) : 0;
  const remaining = Math.max(0, total - sold);
  const isAlmostGone = percentage >= 80;

  return (
    <div className={className}>
      <div className="h-2 overflow-hidden rounded-full bg-gray-200">
        <div
          className={`h-full rounded-full transition-all ${isAlmostGone ? 'bg-red-500' : 'bg-orange-400'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <p className={`mt-1 text-xs ${isAlmostGone ? 'font-medium text-red-600' : 'text-gray-500'}`}>
        {remaining > 0 ? `${remaining} left` : 'Sold out'} · {sold} sold
      </p>
    </div>
  );
}
