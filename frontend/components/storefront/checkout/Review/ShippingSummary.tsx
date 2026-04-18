'use client';

import { MapPin, Truck } from 'lucide-react';
import { useStoreCheckoutStore } from '@/stores/store';

export const ShippingSummary = () => {
  const shippingAddress = useStoreCheckoutStore((s) => s.shippingAddress);
  const shippingMethod = useStoreCheckoutStore((s) => s.shippingMethod);

  const addressParts = [
    shippingAddress.address1,
    shippingAddress.city,
    shippingAddress.district,
    shippingAddress.province,
    shippingAddress.postalCode,
  ].filter(Boolean);

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 text-sm">
        <MapPin className="h-4 w-4 shrink-0 text-gray-400 mt-0.5" />
        <span className="text-gray-900">
          {addressParts.length > 0 ? addressParts.join(', ') : '—'}
        </span>
      </div>
      {shippingMethod && (
        <div className="flex items-center gap-3 text-sm">
          <Truck className="h-4 w-4 shrink-0 text-gray-400" />
          <div>
            <span className="text-gray-900">{shippingMethod.name}</span>
            <span className="ml-2 text-gray-500">₨{shippingMethod.price.toLocaleString()}</span>
          </div>
        </div>
      )}
    </div>
  );
};
