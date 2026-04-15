'use client';

import { useState } from 'react';
import { Pause } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { usePOS } from '../context/POSContext';

const MAX_HELD_SALES = 10;

interface HoldSaleButtonProps {
  className?: string;
}

export function HoldSaleButton({ className }: HoldSaleButtonProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [reason, setReason] = useState('');
  const { cartItems, heldSales, holdSale, closeModal } = usePOS();

  const canHold = cartItems.length > 0 && heldSales.length < MAX_HELD_SALES;

  const handleHold = () => {
    holdSale(reason || undefined);
    setReason('');
    setDialogOpen(false);
    closeModal();
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        disabled={!canHold}
        onClick={() => setDialogOpen(true)}
        className={className}
      >
        <Pause className="mr-1 h-3.5 w-3.5" />
        Hold
        <kbd className="ml-1 hidden rounded bg-gray-100 px-1 text-[10px] text-gray-500 dark:bg-gray-700 sm:inline">
          F4
        </kbd>
      </Button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-xs">
          <DialogHeader>
            <DialogTitle>Hold Sale</DialogTitle>
          </DialogHeader>

          <div className="space-y-3">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {cartItems.length} item{cartItems.length !== 1 && 's'} will be held.
            </p>

            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
                Reason (optional)
              </label>
              <input
                type="text"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g. Customer went to get cash"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
                autoFocus
              />
            </div>

            <p className="text-xs text-gray-500">
              {heldSales.length}/{MAX_HELD_SALES} held sales
            </p>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleHold}>Hold Sale</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
