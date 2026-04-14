'use client';

import { useState } from 'react';
import type { Product } from '@/types/product';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface DeleteProductDialogProps {
  product: Product;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => Promise<void>;
}

export function DeleteProductDialog({
  product,
  open,
  onOpenChange,
  onConfirm,
}: DeleteProductDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async () => {
    setIsDeleting(true);
    try {
      await onConfirm();
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <ConfirmDialog
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={handleConfirm}
      title="Delete Product"
      description={`Are you sure you want to delete "${product.name}"${
        product.sku ? ` (SKU: ${product.sku})` : ''
      }? This action cannot be undone. All associated data including variants, images, and inventory records will be permanently removed.`}
      variant="destructive"
      confirmText="Delete Product"
      cancelText="Cancel"
      isLoading={isDeleting}
    />
  );
}
