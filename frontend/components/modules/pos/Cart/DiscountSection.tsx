'use client';

import { useState } from 'react';
import { Percent } from 'lucide-react';
import { useCartStore } from '@/stores/pos/cart';
import { DiscountModal } from './DiscountModal';

interface DiscountSectionProps {
  amount: number;
  subtotal: number;
}

export function DiscountSection({ amount, subtotal }: DiscountSectionProps) {
  const [showModal, setShowModal] = useState(false);
  const { discount, applyCartDiscount, removeCartDiscount, getItemCount } = useCartStore();
  const isEmpty = getItemCount() === 0;

  return (
    <>
      <div className="flex items-center justify-between text-green-600">
        <div className="flex items-center gap-1">
          <span>Discount</span>
          {!discount && (
            <button
              onClick={() => setShowModal(true)}
              disabled={isEmpty}
              className="ml-1 rounded p-0.5 text-gray-400 transition-colors hover:bg-gray-200 hover:text-gray-600 disabled:cursor-not-allowed disabled:opacity-40 dark:hover:bg-gray-700 dark:hover:text-gray-300"
              aria-label="Apply discount"
              title="Apply cart discount"
            >
              <Percent className="h-3 w-3" />
            </button>
          )}
          {discount && (
            <span className="ml-1 flex items-center gap-1">
              <button
                onClick={() => setShowModal(true)}
                className="text-[10px] text-blue-400 underline hover:text-blue-600"
                title={discount.reason ? `Reason: ${discount.reason}` : undefined}
              >
                Edit
              </button>
              <button
                onClick={removeCartDiscount}
                className="text-[10px] text-red-400 underline hover:text-red-600"
              >
                Remove
              </button>
            </span>
          )}
        </div>
        {amount > 0 ? (
          <span
            title={
              discount
                ? `${discount.type === 'percentage' ? `${discount.value}%` : `₨ ${discount.value}`}${discount.reason ? ` — ${discount.reason}` : ''}`
                : undefined
            }
          >
            -₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
          </span>
        ) : (
          <span className="text-gray-400">₨ 0.00</span>
        )}
      </div>

      <DiscountModal
        open={showModal}
        onClose={() => setShowModal(false)}
        onApply={(d) => {
          applyCartDiscount(d);
          setShowModal(false);
        }}
        onClear={() => {
          removeCartDiscount();
          setShowModal(false);
        }}
        currentDiscount={discount}
        subtotal={subtotal}
      />
    </>
  );
}
