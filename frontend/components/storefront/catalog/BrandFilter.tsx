'use client';

import { useState, useMemo, useCallback } from 'react';
import { cn } from '@/lib/utils';

interface BrandFilterProps {
  brands: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

const INITIAL_VISIBLE = 5;

export function BrandFilter({ brands, selected, onChange }: BrandFilterProps) {
  const [search, setSearch] = useState('');
  const [showAll, setShowAll] = useState(false);

  const filtered = useMemo(() => {
    if (!search.trim()) return brands;
    const q = search.toLowerCase();
    return brands.filter((b) => b.toLowerCase().includes(q));
  }, [brands, search]);

  const visible = showAll ? filtered : filtered.slice(0, INITIAL_VISIBLE);
  const hasMore = filtered.length > INITIAL_VISIBLE;

  const toggle = useCallback(
    (brand: string) => {
      const isSelected = selected.includes(brand);
      onChange(isSelected ? selected.filter((b) => b !== brand) : [...selected, brand]);
    },
    [selected, onChange]
  );

  if (!brands.length) return null;

  return (
    <div className="space-y-3">
      {/* Search */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M9 3.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM2 9a7 7 0 1 1 12.452 4.391l3.328 3.329a.75.75 0 1 1-1.06 1.06l-3.329-3.328A7 7 0 0 1 2 9Z"
            clipRule="evenodd"
          />
        </svg>
        <input
          type="text"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setShowAll(false);
          }}
          placeholder="Search brands..."
          className="w-full rounded-md border border-gray-300 py-2 pl-9 pr-3 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      {/* Brand list */}
      <div className="space-y-1.5">
        {visible.map((brand) => (
          <label
            key={brand}
            className="flex items-center gap-2 cursor-pointer text-sm text-gray-700 hover:text-gray-900 select-none py-0.5"
          >
            <input
              type="checkbox"
              checked={selected.includes(brand)}
              onChange={() => toggle(brand)}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span>{brand}</span>
          </label>
        ))}
      </div>

      {/* Show more/less */}
      {hasMore && !search && (
        <button
          type="button"
          onClick={() => setShowAll((v) => !v)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium transition-colors"
        >
          {showAll ? 'Show less' : `Show more (${filtered.length - INITIAL_VISIBLE})`}
        </button>
      )}

      {filtered.length === 0 && <p className="text-xs text-gray-400">No brands found</p>}
    </div>
  );
}
