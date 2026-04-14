'use client';

import { useState } from 'react';
import { ArrowRightLeft, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { Quote } from '@/types/quotes';

interface ConversionModalProps {
  isOpen: boolean;
  onClose: () => void;
  quote: Quote;
  onConvert: (options: {
    generateInvoice: boolean;
    sendEmail: boolean;
    applyDiscount: boolean;
    orderNotes?: string;
  }) => Promise<void>;
  isConverting?: boolean;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function ConversionModal({
  isOpen,
  onClose,
  quote,
  onConvert,
  isConverting,
}: ConversionModalProps) {
  const [generateInvoice, setGenerateInvoice] = useState(true);
  const [sendEmail, setSendEmail] = useState(true);
  const [applyDiscount, setApplyDiscount] = useState(true);
  const [orderNotes, setOrderNotes] = useState('');

  const handleConvert = async () => {
    await onConvert({
      generateInvoice,
      sendEmail,
      applyDiscount,
      orderNotes: orderNotes || undefined,
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[450px]">
        <DialogHeader>
          <DialogTitle>Convert Quote to Order</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Quote Summary */}
          <div className="rounded-md border p-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Quote</span>
              <span className="font-mono font-medium">{quote.quoteNumber}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Customer</span>
              <span className="font-medium">{quote.customerName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Items</span>
              <span>{quote.items.length}</span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span className="font-medium">Total</span>
              <span className="font-bold">{formatCurrency(quote.total)}</span>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm">
              <Checkbox
                checked={generateInvoice}
                onCheckedChange={(v) => setGenerateInvoice(v as boolean)}
              />
              Generate Invoice
            </label>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox checked={sendEmail} onCheckedChange={(v) => setSendEmail(v as boolean)} />
              Send Confirmation Email
            </label>
            <label className="flex items-center gap-2 text-sm">
              <Checkbox
                checked={applyDiscount}
                onCheckedChange={(v) => setApplyDiscount(v as boolean)}
              />
              Apply Quote Discount
            </label>
          </div>

          {/* Order Notes */}
          <div>
            <label className="text-sm font-medium">Order Notes (optional)</label>
            <Textarea
              value={orderNotes}
              onChange={(e) => setOrderNotes(e.target.value)}
              placeholder="Add notes for the new order..."
              rows={3}
              className="mt-1 resize-none"
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isConverting}>
            Cancel
          </Button>
          <Button onClick={handleConvert} disabled={isConverting}>
            {isConverting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <ArrowRightLeft className="mr-2 h-4 w-4" />
            )}
            Convert to Order
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
