'use client';

import { CartContainer } from '../Cart/CartContainer';
import { CartActionButtons } from '../Cart/CartActionButtons';
import { useCartStore } from '@/stores/pos/cart';
import { usePOS } from '../context/POSContext';

export function CartPanel() {
  const { hasItems, getGrandTotal } = useCartStore();
  const { openModal } = usePOS();

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-hidden">
        <CartContainer />
      </div>

      <CartActionButtons
        cartEmpty={!hasItems()}
        grandTotal={getGrandTotal()}
        onPay={() => openModal('payment')}
        onHold={() => openModal('hold_sale')}
      />
    </div>
  );
}
