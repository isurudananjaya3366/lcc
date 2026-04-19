'use client';

import { useState, useMemo } from 'react';
import { Filter } from 'lucide-react';
import type { FlashSaleProduct } from '@/types/marketing/flash-sale.types';

interface SaleCategoryFilterProps {
  products: FlashSaleProduct[];
  onFilterChange: (category: string | null) => void;
  className?: string;
}

export function SaleCategoryFilter({ products, onFilterChange, className = '' }: SaleCategoryFilterProps) {
  const [selected, setSelected] = useState<string | null>(null);

  const categories = useMemo(() => {
    const seen = new Set<string>();
    const cats: string[] = [];
    for (const p of products) {
      const cat = (p as FlashSaleProduct & { category?: string }).category;
      if (cat && !seen.has(cat)) {
        seen.add(cat);
        cats.push(cat);
      }
    }
    return cats;
  }, [products]);

  if (categories.length === 0) return null;

  const handleSelect = (cat: string | null) => {
    setSelected(cat);
    onFilterChange(cat);
  };

  return (
    <div className={`flex items-center gap-2 overflow-x-auto pb-1 ${className}`}>
      <Filter className="h-4 w-4 flex-shrink-0 text-gray-500" />
      <button
        onClick={() => handleSelect(null)}
        type="button"
        className={`flex-shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
          selected === null
            ? 'bg-red-600 text-white'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => handleSelect(cat)}
          type="button"
          className={`flex-shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
            selected === cat
              ? 'bg-red-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
