'use client';

import { Banknote } from 'lucide-react';
import { PaymentMethodCard } from './PaymentMethodCard';
import { CODConditions } from './CODConditions';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';

export const COD_FEE = 200;

interface CODOptionProps {
  isSelected: boolean;
  onSelect: (method: PaymentMethodType) => void;
  orderSubtotal?: number;
}

export const CODOption = ({ isSelected, onSelect, orderSubtotal = 0 }: CODOptionProps) => {
  return (
    <PaymentMethodCard
      icon={Banknote}
      name="Cash on Delivery"
      description={`₨${COD_FEE} COD delivery fee applies`}
      badge="Most Popular"
      badgeColor="bg-green-100 text-green-700"
      isSelected={isSelected}
      onClick={() => onSelect('cod')}
    >
      <div className="space-y-4">
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">How it works</p>
          <ol className="space-y-1.5 text-sm text-gray-600 list-decimal list-inside">
            <li>Place your order and confirm</li>
            <li>We prepare and ship your items</li>
            <li>Pay cash when you receive the delivery</li>
          </ol>
        </div>

        <div className="rounded-lg bg-amber-50 border border-amber-200 p-3">
          <p className="text-xs text-amber-800 font-medium">
            💡 Keep exact change ready for a smooth delivery experience.
          </p>
        </div>

        {orderSubtotal > 0 && (
          <div className="rounded-lg border border-gray-200 p-3 space-y-1.5">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Subtotal</span>
              <span className="text-gray-900">₨{orderSubtotal.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">COD Fee</span>
              <span className="text-gray-900">₨{COD_FEE.toLocaleString()}</span>
            </div>
            <div className="border-t border-gray-200 pt-1.5 flex justify-between text-sm font-medium">
              <span className="text-gray-700">Total</span>
              <span className="text-gray-900">₨{(orderSubtotal + COD_FEE).toLocaleString()}</span>
            </div>
          </div>
        )}

        <CODConditions orderTotal={orderSubtotal} />
      </div>
    </PaymentMethodCard>
  );
};
