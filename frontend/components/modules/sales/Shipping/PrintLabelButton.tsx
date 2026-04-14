'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Printer, Eye } from 'lucide-react';
import { PrintableLabel } from './PrintableLabel';
import type { OrderAddress } from '@/types/sales';

interface PrintLabelButtonProps {
  disabled?: boolean;
  orderNumber?: string;
  shippingAddress?: OrderAddress;
  carrier?: string;
  serviceLevel?: string;
  trackingNumber?: string;
  itemCount?: number;
  weight?: string;
}

export function PrintLabelButton({
  disabled,
  orderNumber = '',
  shippingAddress,
  carrier = '',
  serviceLevel = 'STANDARD',
  trackingNumber = '',
  itemCount = 0,
  weight,
}: PrintLabelButtonProps) {
  const [showPreview, setShowPreview] = useState(false);

  const handlePrint = () => {
    window.print();
  };

  // Simple mode when no address data is provided
  if (!shippingAddress) {
    return (
      <Button type="button" variant="outline" onClick={handlePrint} disabled={disabled}>
        <Printer className="mr-2 h-4 w-4" />
        Print Label
      </Button>
    );
  }

  return (
    <>
      <Button
        type="button"
        variant="outline"
        onClick={() => setShowPreview(true)}
        disabled={disabled}
      >
        <Eye className="mr-2 h-4 w-4" />
        Preview Label
      </Button>

      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Shipping Label Preview</DialogTitle>
          </DialogHeader>

          <PrintableLabel
            orderNumber={orderNumber}
            shippingAddress={shippingAddress}
            carrier={carrier}
            serviceLevel={serviceLevel}
            trackingNumber={trackingNumber}
            itemCount={itemCount}
            weight={weight}
          />

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPreview(false)}>
              Close
            </Button>
            <Button onClick={handlePrint}>
              <Printer className="mr-2 h-4 w-4" />
              Print
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
