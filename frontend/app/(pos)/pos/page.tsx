'use client';

import { useState } from 'react';
import { POSProvider, usePOS } from '@/components/modules/pos/context/POSContext';
import { POSHeader } from '@/components/modules/pos/Header/POSHeader';
import { POSMainContainer } from '@/components/modules/pos/POSMainContainer';
import { ProductPanel } from '@/components/modules/pos/ProductPanel/ProductPanel';
import { CartPanel } from '@/components/modules/pos/CartPanel/CartPanel';
import { OfflineIndicator } from '@/components/modules/pos/OfflineIndicator';
import { PaymentModal } from '@/components/modules/pos/Payment/PaymentModal';
import { ReceiptModal } from '@/components/modules/pos/Receipt/ReceiptModal';
import { ShiftOpenModal } from '@/components/modules/pos/Shift/ShiftOpenModal';
import { ShiftCloseModal } from '@/components/modules/pos/Shift/ShiftCloseModal';
import { usePOSKeyboardShortcuts } from '@/components/modules/pos/hooks/usePOSKeyboardShortcuts';
import type { POSSale } from '@/components/modules/pos/types';

function POSTerminalContent() {
  usePOSKeyboardShortcuts();
  const { activeModal, closeModal } = usePOS();
  const [completedSale, setCompletedSale] = useState<POSSale | null>(null);

  const handleNewSale = () => {
    setCompletedSale(null);
    closeModal();
  };

  return (
    <>
      <OfflineIndicator />
      <POSHeader />
      <POSMainContainer productPanel={<ProductPanel />} cartPanel={<CartPanel />} />
      <PaymentModal open={activeModal === 'payment'} onClose={closeModal} />
      <ReceiptModal open={activeModal === 'receipt'} onClose={handleNewSale} sale={completedSale} />
      <ShiftOpenModal open={activeModal === 'shift_open'} onClose={closeModal} />
      <ShiftCloseModal open={activeModal === 'shift_close'} onClose={closeModal} />
    </>
  );
}

export default function POSPage() {
  return (
    <main aria-label="POS Terminal" className="flex h-full flex-col">
      <POSProvider>
        <POSTerminalContent />
      </POSProvider>
    </main>
  );
}
