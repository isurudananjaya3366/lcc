'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { PaymentAmount } from './PaymentAmount';
import { PaymentMethodsGrid } from './PaymentMethodsGrid';
import { CashPayment } from './CashPayment';
import { CardPayment } from './CardPayment';
import { BankPayment } from './BankPayment';
import { SplitPaymentToggle } from './SplitPaymentToggle';
import { SplitPaymentInterface } from './SplitPaymentInterface';
import { CustomerSelect } from './CustomerSelect';
import { CompleteSale } from './CompleteSale';
import { useCartStore } from '@/stores/pos/cart';
import { usePOS } from '../context/POSContext';
import type { PaymentMethod, POSPayment, POSCustomer } from '../types';

interface PaymentModalProps {
  open: boolean;
  onClose: () => void;
}

export function PaymentModal({ open, onClose }: PaymentModalProps) {
  const { getGrandTotal } = useCartStore();
  const { customer, setCustomer } = usePOS();
  const grandTotal = getGrandTotal();

  const [selectedMethod, setSelectedMethod] = useState<PaymentMethod>('cash');
  const [payments, setPayments] = useState<POSPayment[]>([]);
  const [isSplit, setIsSplit] = useState(false);
  const [cashAmount, setCashAmount] = useState(0);
  const [cardRef, setCardRef] = useState('');
  const [bankRef, setBankRef] = useState('');

  const paidAmount = payments.reduce((sum, p) => sum + p.amount, 0);
  const remaining = Math.max(0, grandTotal - paidAmount);

  // Reset state when modal opens
  useEffect(() => {
    if (open) {
      setPayments([]);
      setIsSplit(false);
      setCashAmount(0);
      setCardRef('');
      setBankRef('');
      setSelectedMethod('cash');
    }
  }, [open]);

  const addPayment = (payment: Omit<POSPayment, 'id' | 'paidAt'>) => {
    const newPayment: POSPayment = {
      ...payment,
      id: crypto.randomUUID(),
      paidAt: new Date().toISOString(),
    };
    setPayments((prev) => [...prev, newPayment]);
  };

  const removePayment = (paymentId: string) => {
    setPayments((prev) => prev.filter((p) => p.id !== paymentId));
  };

  const handleCashSubmit = (amount: number) => {
    addPayment({
      method: 'cash',
      amount: isSplit ? Math.min(amount, remaining) : grandTotal,
      status: 'completed',
      amountTendered: amount,
      changeDue: Math.max(0, amount - (isSplit ? remaining : grandTotal)),
    });
  };

  const handleCardSubmit = (reference: string) => {
    addPayment({
      method: 'card',
      amount: isSplit ? remaining : grandTotal,
      status: 'completed',
      reference,
    });
  };

  const handleBankSubmit = (reference: string) => {
    addPayment({
      method: 'bank_transfer',
      amount: isSplit ? remaining : grandTotal,
      status: 'completed',
      reference,
    });
  };

  const isFullyPaid = paidAmount >= grandTotal;

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Payment</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Amount Display */}
          <PaymentAmount total={grandTotal} paid={paidAmount} remaining={remaining} />

          {/* Customer Selection */}
          <CustomerSelect
            customer={customer}
            onSelect={(c: POSCustomer | null) => setCustomer(c)}
          />

          {/* Split Toggle */}
          <SplitPaymentToggle enabled={isSplit} onToggle={setIsSplit} />

          {/* Split Payment List */}
          {isSplit && payments.length > 0 && (
            <SplitPaymentInterface
              payments={payments}
              onRemove={removePayment}
              remaining={remaining}
            />
          )}

          {/* Payment Method Selection */}
          {!isFullyPaid && (
            <>
              <PaymentMethodsGrid selected={selectedMethod} onSelect={setSelectedMethod} />

              {/* Method-specific form */}
              {selectedMethod === 'cash' && (
                <CashPayment
                  amount={isSplit ? remaining : grandTotal}
                  cashTendered={cashAmount}
                  onCashChange={setCashAmount}
                  onSubmit={handleCashSubmit}
                />
              )}
              {selectedMethod === 'card' && (
                <CardPayment
                  amount={isSplit ? remaining : grandTotal}
                  reference={cardRef}
                  onReferenceChange={setCardRef}
                  onSubmit={handleCardSubmit}
                />
              )}
              {selectedMethod === 'bank_transfer' && (
                <BankPayment
                  amount={isSplit ? remaining : grandTotal}
                  reference={bankRef}
                  onReferenceChange={setBankRef}
                  onSubmit={handleBankSubmit}
                />
              )}
            </>
          )}

          {/* Complete Sale */}
          {isFullyPaid && (
            <CompleteSale payments={payments} customer={customer} onComplete={onClose} />
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
