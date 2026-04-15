'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import { posService } from '@/services/pos';
import { CategoryTabs } from './CategoryTabs';
import { QuickButtonGrid } from './QuickButtonGrid';
import { usePOS } from '../context/POSContext';
import type { QuickButtonGroup as QBGroup } from '../types';

export function QuickButtons() {
  const [groups, setGroups] = useState<QBGroup[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { addToCart, openModal } = usePOS();

  useEffect(() => {
    setIsLoading(true);
    posService
      .fetchQuickButtonGroups()
      .then((data) => {
        setGroups(data);
        setError(null);
      })
      .catch(() => setError('Failed to load products'))
      .finally(() => setIsLoading(false));
  }, []);

  const categories = [
    { id: 'all', name: 'All' },
    ...groups.map((g) => ({ id: g.id, name: g.name })),
  ];

  const filteredButtons =
    activeCategory === 'all'
      ? groups.flatMap((g) => g.buttons)
      : (groups.find((g) => g.id === activeCategory)?.buttons ?? []);

  const handleButtonClick = (button: QBGroup['buttons'][number]) => {
    if (!button.inStock) return;
    if (button.hasVariants) {
      openModal('variant_select');
      return;
    }
    addToCart({
      productId: button.productId,
      productName: button.label,
      sku: '',
      unitPrice: button.price,
      originalPrice: button.price,
      quantity: button.quickQuantity || 1,
      taxRate: 0,
      isTaxable: true,
      imageUrl: button.imageUrl,
    });
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-400">
        <Loader2 className="h-6 w-6 animate-spin" />
        <p className="mt-2 text-sm">Loading products...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <p className="text-sm text-red-500">{error}</p>
        <button
          onClick={() => {
            setIsLoading(true);
            posService
              .fetchQuickButtonGroups()
              .then((data) => {
                setGroups(data);
                setError(null);
              })
              .catch(() => setError('Failed to load products'))
              .finally(() => setIsLoading(false));
          }}
          className="mt-2 text-sm text-primary underline"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
        Quick Add
      </h3>
      {categories.length > 2 && (
        <CategoryTabs
          categories={categories}
          activeId={activeCategory}
          onSelect={setActiveCategory}
        />
      )}
      <QuickButtonGrid buttons={filteredButtons} onButtonClick={handleButtonClick} />
    </div>
  );
}
