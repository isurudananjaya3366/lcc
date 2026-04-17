import { LowStockWarning } from './LowStockWarning';

interface StockStatusProps {
  inStock: boolean;
  stockQuantity: number;
  lowStockThreshold?: number;
}

export function StockStatus({
  inStock,
  stockQuantity,
  lowStockThreshold = 5,
}: StockStatusProps) {
  if (!inStock || stockQuantity <= 0) {
    return (
      <div className="flex items-center gap-2">
        <span className="inline-block h-2.5 w-2.5 rounded-full bg-red-500" />
        <span className="text-sm font-medium text-red-600">Out of Stock</span>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <span className="inline-block h-2.5 w-2.5 rounded-full bg-green-500" />
        <span className="text-sm font-medium text-green-700">In Stock</span>
      </div>
      {stockQuantity <= lowStockThreshold && (
        <LowStockWarning quantity={stockQuantity} />
      )}
    </div>
  );
}
