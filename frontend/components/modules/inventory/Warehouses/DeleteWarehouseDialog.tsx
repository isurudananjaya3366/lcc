'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, Loader2 } from 'lucide-react';

import type { Warehouse } from '@/types/inventory';
import { warehouseService } from '@/services/api';
import { inventoryKeys } from '@/lib/queryKeys';
import { Button } from '@/components/ui/button';

interface DeleteWarehouseDialogProps {
  warehouse: Warehouse;
  open: boolean;
  onClose: () => void;
}

export function DeleteWarehouseDialog({ warehouse, open, onClose }: DeleteWarehouseDialogProps) {
  const queryClient = useQueryClient();
  const [confirmCode, setConfirmCode] = useState('');

  const hasStock = (warehouse.currentUtilization ?? 0) > 0;
  const canDelete = !warehouse.isPrimary && !hasStock;
  const isConfirmed = confirmCode === warehouse.code;

  const mutation = useMutation({
    mutationFn: () => warehouseService.deleteWarehouse(warehouse.id),
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
        className="mx-4 w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-900"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center gap-2 text-red-600 dark:text-red-400">
          <AlertTriangle className="h-5 w-5" />
          <h2 className="text-lg font-semibold">Delete Warehouse</h2>
        </div>

        {!canDelete ? (
          <>
            <div className="mb-4 rounded-md bg-yellow-50 p-3 text-sm dark:bg-yellow-900/20">
              <p className="font-medium text-yellow-800 dark:text-yellow-400">
                Cannot delete this warehouse:
              </p>
              <ul className="mt-1 list-inside list-disc text-yellow-700 dark:text-yellow-300">
                {warehouse.isPrimary && <li>This is the primary warehouse</li>}
                {hasStock && (
                  <li>This warehouse has {warehouse.currentUtilization} items in stock</li>
                )}
              </ul>
            </div>
            <div className="flex justify-end">
              <Button variant="outline" onClick={onClose}>
                Close
              </Button>
            </div>
          </>
        ) : (
          <>
            <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">
              Are you sure you want to delete <strong>{warehouse.name}</strong>? This action cannot
              be undone.
            </p>

            <div className="mb-4">
              <label
                htmlFor="confirm-code"
                className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Type <strong>{warehouse.code}</strong> to confirm
              </label>
              <input
                id="confirm-code"
                type="text"
                value={confirmCode}
                onChange={(e) => setConfirmCode(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
                placeholder={warehouse.code}
              />
            </div>

            {mutation.isError && (
              <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
                Failed to delete warehouse. Please try again.
              </div>
            )}

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={onClose} disabled={mutation.isPending}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                disabled={!isConfirmed || mutation.isPending}
                onClick={() => mutation.mutate()}
              >
                {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Delete Warehouse
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
