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
import { CashCountInput } from './CashCountInput';
import { ShiftVarianceDisplay } from './ShiftVarianceDisplay';
import { ShiftSummaryDisplay } from './ShiftSummaryDisplay';
import { posService } from '@/services/pos';
import { usePOS } from '../context/POSContext';

interface ShiftCloseModalProps {
  open: boolean;
  onClose: () => void;
}

export function ShiftCloseModal({ open, onClose }: ShiftCloseModalProps) {
  const { currentShift, setShift } = usePOS();
  const [actualCash, setActualCash] = useState(0);
  const [notes, setNotes] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!currentShift) return null;

  const expectedCash = currentShift.expectedCash;
  const variance = actualCash - expectedCash;

  const handleClose = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await posService.closeSession(currentShift.id, {
        closing_cash: actualCash,
        notes,
      });
      setShift(null);
      onClose();
    } catch {
      setError('Failed to close shift. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Close Shift</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Shift Summary */}
          <ShiftSummaryDisplay
            sessionNumber={currentShift.sessionNumber}
            transactionCount={currentShift.transactionCount}
            totalSales={currentShift.totalSales}
            expectedCash={expectedCash}
          />

          {/* Cash Count */}
          <CashCountInput value={actualCash} onChange={setActualCash} />

          {/* Variance */}
          {actualCash > 0 && (
            <ShiftVarianceDisplay expected={expectedCash} actual={actualCash} variance={variance} />
          )}

          {/* Notes */}
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
              Closing Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
              rows={2}
              placeholder="Any notes about the shift..."
            />
          </div>

          {error && <p className="text-center text-sm text-red-500">{error}</p>}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleClose} disabled={isLoading} variant="destructive">
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Closing...
              </>
            ) : (
              'Close Shift'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
