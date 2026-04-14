'use client';

import { useState } from 'react';
import type { ProductVariant } from '@/types/product';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';

interface DeleteVariantDialogProps {
  variant?: ProductVariant | null;
  variantIds?: string[];
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (ids: string[]) => Promise<void>;
}

export function DeleteVariantDialog({
  variant,
  variantIds = [],
  isOpen,
  onClose,
  onConfirm,
}: DeleteVariantDialogProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const isBulk = variantIds.length > 0;
  const ids = isBulk ? variantIds : variant ? [variant.id] : [];

  const handleConfirm = async () => {
    setIsDeleting(true);
    try {
      await onConfirm(ids);
      onClose();
    } finally {
      setIsDeleting(false);
    }
  };

  const title = isBulk ? `Delete ${variantIds.length} Variants` : 'Delete Variant';

  const description = isBulk
    ? `Are you sure you want to delete ${variantIds.length} selected variants? This action cannot be undone and all associated inventory data will be removed.`
    : variant
      ? `Are you sure you want to delete variant "${variant.variantName}" (SKU: ${variant.sku})? This action cannot be undone.`
      : '';

  return (
    <ConfirmDialog
      open={isOpen}
      onOpenChange={(open) => !open && onClose()}
      onConfirm={handleConfirm}
      title={title}
      description={description}
      variant="destructive"
      confirmText={isBulk ? `Delete ${variantIds.length} Variants` : 'Delete Variant'}
      cancelText="Cancel"
      isLoading={isDeleting}
    />
  );
}
