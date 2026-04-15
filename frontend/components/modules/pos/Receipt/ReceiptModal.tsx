'use client';

import { useEffect, useCallback } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { CheckCircle } from 'lucide-react';
import { ReceiptContent } from './ReceiptContent';
import { PrintReceiptButton } from './PrintReceiptButton';
import { EmailReceiptButton } from './EmailReceiptButton';
import { NewSaleButton } from './NewSaleButton';
import type { POSSale } from '../types';

interface ReceiptModalProps {
  open: boolean;
  onClose: () => void;
  sale: POSSale | null;
}

export function ReceiptModal({ open, onClose, sale }: ReceiptModalProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!open) return;
      if (e.key === 'p' || e.key === 'P') {
        e.preventDefault();
        window.print();
      }
    },
    [open]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!sale) return null;

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md print:border-none print:shadow-none">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Sale Complete
          </DialogTitle>
          <p className="text-xs text-gray-500">
            Receipt #{sale.referenceNumber} &bull;{' '}
            {new Date(sale.completedAt ?? sale.createdAt).toLocaleString()}
          </p>
        </DialogHeader>

        {/* Receipt Content */}
        <div className="max-h-[60vh] overflow-y-auto rounded border border-gray-100 bg-white p-4 dark:border-gray-800 dark:bg-gray-900">
          <ReceiptContent sale={sale} />
        </div>

        {/* Actions */}
        <div className="flex gap-2 print:hidden">
          <PrintReceiptButton />
          <EmailReceiptButton receiptId={sale.id} />
          <NewSaleButton onNewSale={onClose} />
        </div>
      </DialogContent>
    </Dialog>
  );
}
