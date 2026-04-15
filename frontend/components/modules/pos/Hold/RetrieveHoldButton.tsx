'use client';

import { useState } from 'react';
import { Clock, Play, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { usePOS } from '../context/POSContext';

interface RetrieveHoldButtonProps {
  className?: string;
}

export function RetrieveHoldButton({ className }: RetrieveHoldButtonProps) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { heldSales, retrieveHeldSale, closeModal } = usePOS();

  const handleRetrieve = (saleId: string) => {
    retrieveHeldSale(saleId);
    setDialogOpen(false);
    closeModal();
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        disabled={heldSales.length === 0}
        onClick={() => setDialogOpen(true)}
        className={className}
      >
        <Play className="mr-1 h-3.5 w-3.5" />
        Retrieve
        {heldSales.length > 0 && (
          <span className="ml-1 rounded-full bg-amber-100 px-1.5 text-[10px] font-bold text-amber-700 dark:bg-amber-900 dark:text-amber-300">
            {heldSales.length}
          </span>
        )}
        <kbd className="ml-1 hidden rounded bg-gray-100 px-1 text-[10px] text-gray-500 dark:bg-gray-700 sm:inline">
          F5
        </kbd>
      </Button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Held Sales ({heldSales.length})</DialogTitle>
          </DialogHeader>

          {heldSales.length === 0 ? (
            <p className="py-4 text-center text-sm text-gray-500">No held sales</p>
          ) : (
            <div className="max-h-64 space-y-2 overflow-y-auto">
              {heldSales.map((sale) => (
                <div
                  key={sale.id}
                  className="flex items-center justify-between rounded-md border border-gray-200 p-3 dark:border-gray-700"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">
                      {sale.items.length} item{sale.items.length !== 1 && 's'}
                      {sale.customer && (
                        <span className="ml-1 text-gray-500">— {sale.customer.name}</span>
                      )}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <Clock className="h-3 w-3" />
                      <span>
                        {new Date(sale.createdAt).toLocaleTimeString('en-LK', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                      {sale.heldReason && (
                        <span className="truncate text-gray-400">— {sale.heldReason}</span>
                      )}
                    </div>
                  </div>
                  <div className="ml-2 flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRetrieve(sale.id)}
                      title="Retrieve sale"
                    >
                      <Play className="h-4 w-4 text-green-600" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
