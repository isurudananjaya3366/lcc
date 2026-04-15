'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, CheckCircle2 } from 'lucide-react';

import type { StockTransfer } from '@/types/inventory';
import inventoryService from '@/services/api/inventoryService';
import { inventoryKeys } from '@/lib/queryKeys';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ReceiveTransferDialogProps {
  transfer: StockTransfer;
  open: boolean;
  onClose: () => void;
}

export function ReceiveTransferDialog({ transfer, open, onClose }: ReceiveTransferDialogProps) {
  const queryClient = useQueryClient();

  const [receivedQuantities, setReceivedQuantities] = useState<Record<string, number>>(() =>
    Object.fromEntries(transfer.items.map((item) => [item.productId, item.quantity]))
  );

  const mutation = useMutation({
    mutationFn: () =>
      inventoryService.completeStockTransfer(
        transfer.id,
        transfer.items.map((item) => ({
          productId: item.productId,
          variantId: item.variantId,
          quantityReceived: receivedQuantities[item.productId] ?? item.quantity,
        }))
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
      onClose();
    },
  });

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={onClose}
    >
      <div
        className="mx-4 w-full max-w-lg rounded-lg bg-white p-6 shadow-xl dark:bg-gray-900"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-green-500" />
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Receive Transfer
          </h2>
        </div>

        <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
          Transfer {transfer.transferNumber} — Verify received quantities for each item.
        </p>

        <div className="mb-6 max-h-64 space-y-3 overflow-y-auto">
          {transfer.items.map((item) => {
            const received = receivedQuantities[item.productId] ?? 0;
            const diff = received - item.quantity;
            return (
              <div
                key={item.productId}
                className="flex items-center gap-3 rounded-md border border-gray-200 p-3 dark:border-gray-700"
              >
                <div className="flex-1">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                    {item.productId}
                  </span>
                  <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                    Sent: {item.quantity}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    min={0}
                    max={item.quantity}
                    value={received}
                    onChange={(e) =>
                      setReceivedQuantities((prev) => ({
                        ...prev,
                        [item.productId]: Number(e.target.value),
                      }))
                    }
                    className="w-20"
                  />
                  {diff !== 0 && (
                    <span
                      className={`text-xs font-medium ${
                        diff < 0 ? 'text-red-500' : 'text-yellow-500'
                      }`}
                    >
                      {diff > 0 ? '+' : ''}
                      {diff}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {mutation.isError && (
          <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
            Failed to receive transfer. Please try again.
          </div>
        )}

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={onClose} disabled={mutation.isPending}>
            Cancel
          </Button>
          <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
            {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Confirm Receipt
          </Button>
        </div>
      </div>
    </div>
  );
}
