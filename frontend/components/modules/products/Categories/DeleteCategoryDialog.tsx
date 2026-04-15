'use client';

import { useState } from 'react';
import { AlertTriangle, FolderTree, Package } from 'lucide-react';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import type { ProductCategory } from '@/types/product';

interface DeleteCategoryDialogProps {
  category: ProductCategory | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (options: DeleteOptions) => void;
  categories: ProductCategory[];
  isLoading?: boolean;
}

interface DeleteOptions {
  categoryId: string;
  productAction: 'move_parent' | 'move_other' | 'uncategorize';
  moveProductsTo?: string;
  childrenAction: 'flatten' | 'delete';
  confirmed: boolean;
}

export function DeleteCategoryDialog({
  category,
  isOpen,
  onClose,
  onConfirm,
  categories,
  isLoading,
}: DeleteCategoryDialogProps) {
  const [productAction, setProductAction] = useState<DeleteOptions['productAction']>('move_parent');
  const [moveProductsTo, setMoveProductsTo] = useState<string | undefined>();
  const [childrenAction, setChildrenAction] = useState<DeleteOptions['childrenAction']>('flatten');
  const [confirmed, setConfirmed] = useState(false);

  if (!category) return null;

  const hasProducts = category.productCount > 0;
  const hasChildren = categories.some((c) => c.parentId === category.id);
  const otherCategories = categories.filter((c) => c.id !== category.id);

  const handleConfirm = () => {
    onConfirm({
      categoryId: category.id,
      productAction,
      moveProductsTo: productAction === 'move_other' ? moveProductsTo : undefined,
      childrenAction,
      confirmed,
    });
  };

  const isSimpleDelete = !hasProducts && !hasChildren;

  return (
    <ConfirmDialog
      open={isOpen}
      onOpenChange={(open) => {
        if (!open) {
          onClose();
          setConfirmed(false);
          setProductAction('move_parent');
          setChildrenAction('flatten');
        }
      }}
      onConfirm={handleConfirm}
      title={`Delete "${category.name}"?`}
      description={
        isSimpleDelete
          ? 'This category has no products or subcategories. It will be permanently deleted.'
          : 'Please select how to handle the associated products and subcategories before deleting.'
      }
      variant="destructive"
      confirmText="Delete Category"
      isLoading={isLoading}
    >
      {!isSimpleDelete && (
        <div className="space-y-4 py-2">
          {hasProducts && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <Package className="h-4 w-4 text-amber-500" />
                <span>
                  {category.productCount} product{category.productCount > 1 ? 's' : ''} in this
                  category
                </span>
              </div>

              <div className="space-y-2 pl-6">
                <Label className="text-sm">What should happen to these products?</Label>
                <Select
                  value={productAction}
                  onValueChange={(v) => setProductAction(v as DeleteOptions['productAction'])}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {category.parentId && (
                      <SelectItem value="move_parent">Move to parent category</SelectItem>
                    )}
                    <SelectItem value="move_other">Move to another category</SelectItem>
                    <SelectItem value="uncategorize">Remove category (uncategorize)</SelectItem>
                  </SelectContent>
                </Select>

                {productAction === 'move_other' && (
                  <Select value={moveProductsTo} onValueChange={setMoveProductsTo}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select target category..." />
                    </SelectTrigger>
                    <SelectContent>
                      {otherCategories.map((c) => (
                        <SelectItem key={c.id} value={c.id}>
                          {c.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>
          )}

          {hasChildren && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm font-medium">
                <FolderTree className="h-4 w-4 text-amber-500" />
                <span>This category has subcategories</span>
              </div>

              <div className="space-y-2 pl-6">
                <Label className="text-sm">What should happen to subcategories?</Label>
                <Select
                  value={childrenAction}
                  onValueChange={(v) => setChildrenAction(v as DeleteOptions['childrenAction'])}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="flatten">Move to parent level</SelectItem>
                    <SelectItem value="delete">Delete all subcategories</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          <div className="flex items-start gap-2 rounded-md border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-950/30">
            <AlertTriangle className="h-4 w-4 mt-0.5 text-amber-600 shrink-0" />
            <p className="text-xs text-amber-700 dark:text-amber-400">
              This action cannot be undone. Please review your selections carefully.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox
              id="confirm-delete"
              checked={confirmed}
              onCheckedChange={(v) => setConfirmed(v === true)}
            />
            <Label htmlFor="confirm-delete" className="text-sm cursor-pointer">
              I understand this will permanently delete this category
            </Label>
          </div>
        </div>
      )}
    </ConfirmDialog>
  );
}
