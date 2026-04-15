'use client';

import { useState, useRef, useEffect, useCallback } from 'react';

interface CashCountInputProps {
  value: number;
  onChange: (value: number) => void;
}

interface Denomination {
  label: string;
  value: number;
}

const DENOMINATIONS: Denomination[] = [
  { label: '₨ 5,000', value: 5000 },
  { label: '₨ 2,000', value: 2000 },
  { label: '₨ 1,000', value: 1000 },
  { label: '₨ 500', value: 500 },
  { label: '₨ 100', value: 100 },
  { label: '₨ 50', value: 50 },
  { label: '₨ 20', value: 20 },
  { label: '₨ 10', value: 10 },
  { label: '₨ 5', value: 5 },
  { label: '₨ 2', value: 2 },
  { label: '₨ 1', value: 1 },
];

export function CashCountInput({ value, onChange }: CashCountInputProps) {
  const [counts, setCounts] = useState<Record<number, number>>({});
  const [activeIdx, setActiveIdx] = useState(0);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Auto-focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  const recalcTotal = useCallback(
    (newCounts: Record<number, number>) => {
      const total = Object.entries(newCounts).reduce(
        (sum, [denom, qty]) => sum + Number(denom) * qty,
        0
      );
      onChange(total);
    },
    [onChange]
  );

  const updateCount = (denomination: number, count: number) => {
    const clamped = Math.max(0, Math.min(999, count));
    const newCounts = { ...counts, [denomination]: clamped };
    setCounts(newCounts);
    recalcTotal(newCounts);
  };

  const clearAll = () => {
    setCounts({});
    onChange(0);
    inputRefs.current[0]?.focus();
    setActiveIdx(0);
  };

  const handleKeyDown = (e: React.KeyboardEvent, idx: number) => {
    if (e.key === 'Enter' || (e.key === 'Tab' && !e.shiftKey)) {
      if (idx < DENOMINATIONS.length - 1) {
        e.preventDefault();
        inputRefs.current[idx + 1]?.focus();
        setActiveIdx(idx + 1);
      }
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      const next = Math.min(idx + 1, DENOMINATIONS.length - 1);
      inputRefs.current[next]?.focus();
      setActiveIdx(next);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const prev = Math.max(idx - 1, 0);
      inputRefs.current[prev]?.focus();
      setActiveIdx(prev);
    } else if (e.key === 'Escape') {
      const denom = DENOMINATIONS[idx]!.value;
      updateCount(denom, 0);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-medium text-gray-700 dark:text-gray-300">Cash Count</label>
        <div className="flex items-center gap-2">
          <button
            onClick={clearAll}
            className="text-[10px] text-red-400 underline hover:text-red-600"
          >
            Clear All
          </button>
          <span className="text-sm font-bold text-gray-900 dark:text-gray-100">
            ₨ {value.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>
      <div className="max-h-48 space-y-1 overflow-y-auto">
        {DENOMINATIONS.map((d, idx) => (
          <div
            key={d.value}
            className={`flex items-center justify-between gap-2 rounded px-1 ${
              activeIdx === idx ? 'bg-blue-50 dark:bg-blue-950' : ''
            }`}
          >
            <span className="w-20 text-xs text-gray-600 dark:text-gray-400">{d.label}</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => updateCount(d.value, (counts[d.value] ?? 0) - 1)}
                className="rounded border border-gray-300 px-1.5 py-0.5 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                tabIndex={-1}
              >
                -
              </button>
              <input
                ref={(el) => {
                  inputRefs.current[idx] = el;
                }}
                type="number"
                value={counts[d.value] ?? 0}
                onChange={(e) => updateCount(d.value, parseInt(e.target.value, 10) || 0)}
                onFocus={() => setActiveIdx(idx)}
                onKeyDown={(e) => handleKeyDown(e, idx)}
                className="w-12 rounded border border-gray-300 px-1 py-0.5 text-center text-xs dark:border-gray-600 dark:bg-gray-800"
                min={0}
                max={999}
              />
              <button
                onClick={() => updateCount(d.value, (counts[d.value] ?? 0) + 1)}
                className="rounded border border-gray-300 px-1.5 py-0.5 text-xs text-gray-600 hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700"
                tabIndex={-1}
              >
                +
              </button>
              <span className="w-16 text-right text-xs tabular-nums text-gray-500">
                {((counts[d.value] ?? 0) * d.value).toLocaleString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
