'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { OpeningCashInput } from './OpeningCashInput';
import { posService } from '@/services/pos';
import { usePOS } from '../context/POSContext';

interface ShiftOpenModalProps {
  open: boolean;
  onClose: () => void;
}

export function ShiftOpenModal({ open, onClose }: ShiftOpenModalProps) {
  const [openingCash, setOpeningCash] = useState(0);
  const [notes, setNotes] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setShift } = usePOS();

  const handleOpen = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const session = await posService.openSession('default', openingCash);
      setShift({
        ...session,
        openingCash,
        expectedCash: openingCash,
      });
      onClose();
    } catch {
      setError('Failed to open shift. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-sm" onPointerDownOutside={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle>Open Shift</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <OpeningCashInput value={openingCash} onChange={setOpeningCash} />

          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
              rows={2}
              placeholder="Opening notes..."
            />
          </div>

          {error && <p className="text-center text-sm text-red-500">{error}</p>}
        </div>

        <DialogFooter>
          <Button onClick={handleOpen} disabled={isLoading} className="w-full">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Opening...
              </>
            ) : (
              'Open Shift'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
