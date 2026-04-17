'use client';

import { cn } from '@/lib/utils';

interface AvailabilityFilterProps {
  inStock: boolean;
  onSale: boolean;
  onInStockChange: (v: boolean) => void;
  onOnSaleChange: (v: boolean) => void;
}

interface ToggleRowProps {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
  activeColor?: string;
}

function ToggleRow({ label, checked, onChange, activeColor = 'bg-blue-600' }: ToggleRowProps) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <span className="text-sm text-gray-700">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          'relative inline-flex h-6 w-10 flex-shrink-0 rounded-full transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
          checked ? activeColor : 'bg-gray-200'
        )}
      >
        <span
          aria-hidden="true"
          className={cn(
            'inline-block h-4 w-4 rounded-full bg-white shadow transition-transform duration-200 mt-1',
            checked ? 'translate-x-5 ml-0' : 'translate-x-1'
          )}
        />
      </button>
    </div>
  );
}

export function AvailabilityFilter({
  inStock,
  onSale,
  onInStockChange,
  onOnSaleChange,
}: AvailabilityFilterProps) {
  return (
    <div className="space-y-2">
      <ToggleRow
        label="In Stock"
        checked={inStock}
        onChange={onInStockChange}
        activeColor="bg-blue-600"
      />
      <ToggleRow
        label="On Sale"
        checked={onSale}
        onChange={onOnSaleChange}
        activeColor="bg-red-600"
      />
    </div>
  );
}
