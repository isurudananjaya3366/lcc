interface StockIndicatorProps {
  quantity: number;
  reorderPoint?: number;
  variant?: 'badge' | 'dot' | 'overlay';
}

function getStockStatus(quantity: number, reorderPoint: number) {
  if (quantity <= 0)
    return {
      label: 'Out of Stock',
      color: 'text-red-500',
      bg: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      dot: 'bg-red-500',
    };
  if (quantity <= reorderPoint)
    return {
      label: 'Low Stock',
      color: 'text-yellow-500',
      bg: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      dot: 'bg-yellow-500',
    };
  return {
    label: 'In Stock',
    color: 'text-green-500',
    bg: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    dot: 'bg-green-500',
  };
}

export function StockIndicator({
  quantity,
  reorderPoint = 10,
  variant = 'badge',
}: StockIndicatorProps) {
  const status = getStockStatus(quantity, reorderPoint);

  if (variant === 'dot') {
    return (
      <span
        className={`inline-block h-2 w-2 rounded-full ${status.dot}`}
        title={status.label}
        aria-label={status.label}
      />
    );
  }

  if (variant === 'overlay') {
    if (quantity > 0) return null;
    return (
      <div className="absolute inset-0 flex items-center justify-center bg-gray-900/60">
        <span className="rounded bg-red-600 px-2 py-0.5 text-[10px] font-bold uppercase text-white">
          Out of Stock
        </span>
      </div>
    );
  }

  // badge variant
  return (
    <span
      className={`inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-medium ${status.bg}`}
    >
      {status.label}
    </span>
  );
}
