interface SubtotalDisplayProps {
  amount: number;
}

export function SubtotalDisplay({ amount }: SubtotalDisplayProps) {
  return (
    <div className="flex justify-between text-gray-600 dark:text-gray-400">
      <span>Subtotal</span>
      <span>₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
    </div>
  );
}
