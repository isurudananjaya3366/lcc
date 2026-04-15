'use client';

interface QuickAmountsProps {
  amount: number;
  onSelect: (value: number) => void;
}

function roundUp(value: number, unit: number): number {
  return Math.ceil(value / unit) * unit;
}

export function QuickAmounts({ amount, onSelect }: QuickAmountsProps) {
  const quickValues = [
    { label: 'Exact', value: amount },
    { label: `₨ ${roundUp(amount, 100).toLocaleString()}`, value: roundUp(amount, 100) },
    { label: `₨ ${roundUp(amount, 500).toLocaleString()}`, value: roundUp(amount, 500) },
    { label: `₨ ${roundUp(amount, 1000).toLocaleString()}`, value: roundUp(amount, 1000) },
  ];

  // Remove duplicates (e.g., when amount is exactly 100)
  const unique = quickValues.filter((v, i, arr) => arr.findIndex((a) => a.value === v.value) === i);

  return (
    <div className="flex flex-wrap gap-1.5">
      {unique.map((q) => (
        <button
          key={q.value}
          onClick={() => onSelect(q.value)}
          className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 transition-colors hover:border-primary hover:text-primary dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:border-primary"
        >
          {q.label}
        </button>
      ))}
    </div>
  );
}
