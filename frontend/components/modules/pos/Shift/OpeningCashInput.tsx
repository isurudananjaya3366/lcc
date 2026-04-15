'use client';

interface OpeningCashInputProps {
  value: number;
  onChange: (value: number) => void;
}

const QUICK_AMOUNTS = [5000, 10000, 20000, 50000];

export function OpeningCashInput({ value, onChange }: OpeningCashInputProps) {
  return (
    <div className="space-y-2">
      <label className="block text-xs font-medium text-gray-700 dark:text-gray-300">
        Opening Cash (₨)
      </label>
      <input
        type="number"
        value={value || ''}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        placeholder="0.00"
        className="w-full rounded-md border border-gray-300 px-3 py-2 text-lg font-bold dark:border-gray-600 dark:bg-gray-800"
        min={0}
        step={0.01}
      />
      <div className="flex flex-wrap gap-1.5">
        {QUICK_AMOUNTS.map((amt) => (
          <button
            key={amt}
            onClick={() => onChange(amt)}
            className="rounded-full border border-gray-200 px-3 py-1 text-xs font-medium text-gray-700 transition-colors hover:border-primary hover:text-primary dark:border-gray-700 dark:text-gray-300"
          >
            ₨ {amt.toLocaleString()}
          </button>
        ))}
      </div>
    </div>
  );
}
