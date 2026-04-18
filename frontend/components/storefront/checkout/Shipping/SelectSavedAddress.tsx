'use client';

import { MapPin, Check } from 'lucide-react';
import type { ShippingAddress } from '@/types/storefront/checkout.types';

interface SelectSavedAddressProps {
  address: ShippingAddress & { id: string; name?: string; phone?: string };
  selected: boolean;
  onSelect: (address: ShippingAddress & { id: string }) => void;
}

export const SelectSavedAddress = ({ address, selected, onSelect }: SelectSavedAddressProps) => {
  const formatted = [
    address.address1,
    address.address2,
    address.city,
    address.district,
    address.province,
    address.postalCode,
  ]
    .filter(Boolean)
    .join(', ');

  return (
    <button
      type="button"
      onClick={() => onSelect(address)}
      className={`w-full flex items-start gap-3 rounded-lg border-2 p-4 text-left transition-colors ${
        selected ? 'border-blue-600 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
    >
      <div
        className={`mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          selected ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'
        }`}
      >
        {selected ? <Check className="h-4 w-4" /> : <MapPin className="h-4 w-4" />}
      </div>
      <div className="flex-1 min-w-0">
        {address.name && <p className="text-sm font-medium text-gray-900">{address.name}</p>}
        <p className="text-sm text-gray-600 truncate">{formatted}</p>
        {address.phone && <p className="text-xs text-muted-foreground mt-1">{address.phone}</p>}
      </div>
      <div
        className={`mt-1 h-4 w-4 shrink-0 rounded-full border-2 ${
          selected ? 'border-blue-600 bg-blue-600' : 'border-gray-300'
        }`}
      >
        {selected && (
          <div className="h-full w-full flex items-center justify-center">
            <div className="h-1.5 w-1.5 rounded-full bg-white" />
          </div>
        )}
      </div>
    </button>
  );
};
