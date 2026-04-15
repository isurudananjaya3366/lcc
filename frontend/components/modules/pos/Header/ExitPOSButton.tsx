'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { LogOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { usePOS } from '../context/POSContext';

export function ExitPOSButton() {
  const [showDialog, setShowDialog] = useState(false);
  const router = useRouter();
  const { cartItems, holdSale } = usePOS();

  const hasItems = cartItems.length > 0;

  const handleExitClick = () => {
    if (hasItems) {
      setShowDialog(true);
    } else {
      router.push('/dashboard');
    }
  };

  const handleExit = () => {
    setShowDialog(false);
    router.push('/dashboard');
  };

  const handleHoldAndExit = () => {
    holdSale('Exiting POS');
    setShowDialog(false);
    router.push('/dashboard');
  };

  return (
    <>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleExitClick}
        className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100"
        aria-label="Exit POS Terminal"
      >
        <LogOut className="mr-2 h-4 w-4" />
        Exit POS
      </Button>

      <Dialog open={showDialog} onOpenChange={setShowDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Exit POS Terminal?</DialogTitle>
            <DialogDescription>
              You have {cartItems.length} item{cartItems.length !== 1 ? 's' : ''} in the cart. Would
              you like to hold the current sale or discard it?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="flex gap-2 sm:justify-end">
            <Button variant="outline" onClick={() => setShowDialog(false)}>
              Cancel
            </Button>
            <Button variant="secondary" onClick={handleHoldAndExit}>
              Hold &amp; Exit
            </Button>
            <Button variant="destructive" onClick={handleExit}>
              Discard &amp; Exit
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
