'use client';

import { useState } from 'react';
import type { ProductVariant } from '@/types/product';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2 } from 'lucide-react';

interface BulkUpdate {
  priceOperation?:
    | 'set'
    | 'increase_amount'
    | 'increase_percent'
    | 'decrease_amount'
    | 'decrease_percent';
  priceValue?: number;
  stockOperation?: 'set' | 'add' | 'subtract';
  stockValue?: number;
  status?: 'active' | 'inactive';
}

interface VariantBulkEditProps {
  selectedVariants: ProductVariant[];
  onClose: () => void;
  onApply: (updates: BulkUpdate) => Promise<void>;
}

export function VariantBulkEdit({ selectedVariants, onClose, onApply }: VariantBulkEditProps) {
  const [updates, setUpdates] = useState<BulkUpdate>({});
  const [applying, setApplying] = useState(false);

  const handleApply = async () => {
    setApplying(true);
    try {
      await onApply(updates);
      onClose();
    } finally {
      setApplying(false);
    }
  };

  const hasChanges = updates.priceOperation || updates.stockOperation || updates.status;

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Bulk Edit Variants</DialogTitle>
          <DialogDescription>
            Apply changes to {selectedVariants.length} selected variant
            {selectedVariants.length !== 1 ? 's' : ''}.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Price Operations */}
          <div className="space-y-2">
            <Label className="font-medium">Price</Label>
            <div className="flex items-center gap-2">
              <Select
                value={updates.priceOperation || ''}
                onValueChange={(v) =>
                  setUpdates((prev) => ({
                    ...prev,
                    priceOperation: v as BulkUpdate['priceOperation'],
                  }))
                }
              >
                <SelectTrigger className="w-44">
                  <SelectValue placeholder="No change" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="set">Set exact price</SelectItem>
                  <SelectItem value="increase_amount">Increase by amount</SelectItem>
                  <SelectItem value="increase_percent">Increase by %</SelectItem>
                  <SelectItem value="decrease_amount">Decrease by amount</SelectItem>
                  <SelectItem value="decrease_percent">Decrease by %</SelectItem>
                </SelectContent>
              </Select>
              {updates.priceOperation && (
                <Input
                  type="number"
                  min={0}
                  step={0.01}
                  value={updates.priceValue ?? ''}
                  onChange={(e) =>
                    setUpdates((prev) => ({
                      ...prev,
                      priceValue: parseFloat(e.target.value) || 0,
                    }))
                  }
                  className="w-32"
                  placeholder={updates.priceOperation.includes('percent') ? 'Percentage' : 'Amount'}
                />
              )}
            </div>
          </div>

          {/* Stock Operations */}
          <div className="space-y-2">
            <Label className="font-medium">Stock</Label>
            <div className="flex items-center gap-2">
              <Select
                value={updates.stockOperation || ''}
                onValueChange={(v) =>
                  setUpdates((prev) => ({
                    ...prev,
                    stockOperation: v as BulkUpdate['stockOperation'],
                  }))
                }
              >
                <SelectTrigger className="w-44">
                  <SelectValue placeholder="No change" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="set">Set exact quantity</SelectItem>
                  <SelectItem value="add">Add to stock</SelectItem>
                  <SelectItem value="subtract">Subtract from stock</SelectItem>
                </SelectContent>
              </Select>
              {updates.stockOperation && (
                <Input
                  type="number"
                  min={0}
                  value={updates.stockValue ?? ''}
                  onChange={(e) =>
                    setUpdates((prev) => ({
                      ...prev,
                      stockValue: parseInt(e.target.value) || 0,
                    }))
                  }
                  className="w-32"
                  placeholder="Quantity"
                />
              )}
            </div>
          </div>

          {/* Status */}
          <div className="space-y-2">
            <Label className="font-medium">Status</Label>
            <Select
              value={updates.status || ''}
              onValueChange={(v) =>
                setUpdates((prev) => ({
                  ...prev,
                  status: v as BulkUpdate['status'],
                }))
              }
            >
              <SelectTrigger className="w-44">
                <SelectValue placeholder="No change" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Set Active</SelectItem>
                <SelectItem value="inactive">Set Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={applying}>
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={applying || !hasChanges}>
            {applying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Apply Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
