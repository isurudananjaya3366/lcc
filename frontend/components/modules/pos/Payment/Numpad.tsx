'use client';

import { useState, useCallback } from 'react';
import { Delete } from 'lucide-react';

interface NumpadProps {
  value: number;
  onChange: (value: number) => void;
}

export function Numpad({ value, onChange }: NumpadProps) {
  const [displayStr, setDisplayStr] = useState(value > 0 ? String(value) : '');

  const handleKey = useCallback(
    (key: string) => {
      let next: string;
      if (key === 'C') {
        next = '';
      } else if (key === '⌫') {
        next = displayStr.slice(0, -1);
      } else if (key === '.') {
        if (displayStr.includes('.')) return;
        next = displayStr + '.';
      } else {
        // Limit decimal places to 2
        const parts = displayStr.split('.');
        if (parts[1] && parts[1].length >= 2) return;
        next = displayStr + key;
      }
      setDisplayStr(next);
      onChange(parseFloat(next) || 0);
    },
    [displayStr, onChange]
  );

  const keys = [
    ['7', '8', '9'],
    ['4', '5', '6'],
    ['1', '2', '3'],
    ['C', '0', '.'],
  ];

  return (
    <div className="grid grid-cols-4 gap-1.5">
      {keys.flat().map((key) => (
        <button
          key={key}
          onClick={() => handleKey(key)}
          className={`rounded-md border px-3 py-2.5 text-sm font-medium transition-colors ${
            key === 'C'
              ? 'border-red-200 bg-red-50 text-red-600 hover:bg-red-100 dark:border-red-800 dark:bg-red-950 dark:text-red-400'
              : 'border-gray-200 bg-white text-gray-900 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700'
          }`}
        >
          {key}
        </button>
      ))}
      <button
        onClick={() => handleKey('⌫')}
        className="rounded-md border border-gray-200 bg-white px-3 py-2.5 text-gray-500 transition-colors hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700"
        aria-label="Backspace"
      >
        <Delete className="mx-auto h-4 w-4" />
      </button>
    </div>
  );
}
