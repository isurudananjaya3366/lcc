interface TaxDisplayProps {
  amount: number;
  rate: number;
  name: string;
}

export function TaxDisplay({ amount, rate, name }: TaxDisplayProps) {
  if (rate <= 0) return null;

  return (
    <div className="flex justify-between text-gray-600 dark:text-gray-400">
      <span>
        {name} ({rate}%)
      </span>
      <span>₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}</span>
    </div>
  );
}
