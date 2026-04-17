interface LowStockWarningProps {
  quantity: number;
}

export function LowStockWarning({ quantity }: LowStockWarningProps) {
  return (
    <p className="text-sm font-medium text-amber-600">
      ⚠ Only {quantity} left in stock — order soon!
    </p>
  );
}
