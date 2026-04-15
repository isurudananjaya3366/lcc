'use client';

import { useState } from 'react';
import { Trash2 } from 'lucide-react';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface ClearCartDialogProps {
  onConfirm: () => void;
}

export function ClearCartDialog({ onConfirm }: ClearCartDialogProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="rounded p-1 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-950"
        aria-label="Clear cart"
      >
        <Trash2 className="h-4 w-4" />
      </button>

      <ConfirmDialog
        open={open}
        onOpenChange={setOpen}
        onConfirm={() => {
          onConfirm();
          setOpen(false);
        }}
        title="Clear Cart"
        description="Are you sure you want to remove all items from the cart? This action cannot be undone."
        variant="destructive"
        confirmText="Clear All"
      />
    </>
  );
}
