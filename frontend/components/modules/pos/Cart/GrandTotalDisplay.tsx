interface GrandTotalDisplayProps {
  amount: number;
}

export function GrandTotalDisplay({ amount }: GrandTotalDisplayProps) {
  return (
    <div className="flex justify-between text-base font-bold text-gray-900 dark:text-gray-100">
      <span>Total</span>
      <span>₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
    </div>
  );
}
