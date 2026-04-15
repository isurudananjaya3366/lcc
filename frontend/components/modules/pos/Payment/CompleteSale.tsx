'use client';

import { useState } from 'react';
import { CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { posService } from '@/services/pos';
import { useCartStore } from '@/stores/pos/cart';
import { usePOS } from '../context/POSContext';
import type { POSPayment, POSCustomer } from '../types';

interface CompleteSaleProps {
  payments: POSPayment[];
  customer: POSCustomer | null;
  onComplete: () => void;
}

export function CompleteSale({ payments, customer, onComplete }: CompleteSaleProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { items, getSubtotal, getDiscountTotal, getTaxTotal, getGrandTotal, clearCart } =
    useCartStore();
  const { openModal } = usePOS();

  const handleComplete = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      // Build sale payload
      const saleData = {
        items: items.map((item) => ({
          product_id: item.productId,
          variant_id: item.variantId,
          quantity: item.quantity,
          unit_price: item.unitPrice,
          discount_amount: item.discountAmount,
          tax_amount: item.taxAmount,
          line_total: item.lineTotal,
        })),
        customer_id: customer?.id,
        payments: payments.map((p) => ({
          method: p.method,
          amount: p.amount,
          reference: p.reference,
          authorization_code: p.authorizationCode,
        })),
        subtotal: getSubtotal(),
        discount_amount: getDiscountTotal(),
        tax_amount: getTaxTotal(),
        grand_total: getGrandTotal(),
      };

      await posService.completePayment(String(Date.now()));

      // Clear cart and show receipt
      clearCart();
      onComplete();
      openModal('receipt');
    } catch {
      setError('Failed to complete sale. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 rounded-md bg-green-50 px-3 py-2 text-green-700 dark:bg-green-950 dark:text-green-300">
        <CheckCircle className="h-5 w-5" />
        <p className="text-sm font-medium">Payment received in full</p>
      </div>

      {error && <p className="text-center text-sm text-red-500">{error}</p>}

      <Button className="w-full" size="lg" onClick={handleComplete} disabled={isProcessing}>
        {isProcessing ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          'Complete Sale'
        )}
      </Button>
    </div>
  );
}
