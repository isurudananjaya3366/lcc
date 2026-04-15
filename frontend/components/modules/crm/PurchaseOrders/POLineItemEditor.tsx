'use client';

import { Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableFooter,
} from '@/components/ui/table';

export interface LineItem {
  productId: string;
  variantId?: string;
  quantity: number;
  unitCost: number;
}

interface POLineItemEditorProps {
  items: LineItem[];
  onChange: (items: LineItem[]) => void;
  error?: string;
}

export function POLineItemEditor({ items, onChange, error }: POLineItemEditorProps) {
  function addItem() {
    onChange([...items, { productId: '', quantity: 1, unitCost: 0 }]);
  }

  function removeItem(index: number) {
    onChange(items.filter((_, i) => i !== index));
  }

  function updateItem(index: number, field: keyof LineItem, value: string | number) {
    const updated = items.map((item, i) => {
      if (i !== index) return item;
      return { ...item, [field]: value };
    });
    onChange(updated);
  }

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unitCost, 0);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label>Line Items *</Label>
        <Button type="button" variant="outline" size="sm" onClick={addItem}>
          <Plus className="mr-1 h-3 w-3" />
          Add Item
        </Button>
      </div>

      {items.length > 0 ? (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product ID</TableHead>
                <TableHead className="w-[100px]">Qty</TableHead>
                <TableHead className="w-[140px]">Unit Cost (₨)</TableHead>
                <TableHead className="w-[120px] text-right">Total</TableHead>
                <TableHead className="w-[50px]" />
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item, idx) => (
                <TableRow key={idx}>
                  <TableCell>
                    <Input
                      value={item.productId}
                      onChange={(e) => updateItem(idx, 'productId', e.target.value)}
                      placeholder="Enter product ID"
                      className="h-8"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      min={1}
                      value={item.quantity}
                      onChange={(e) => updateItem(idx, 'quantity', Number(e.target.value))}
                      className="h-8"
                    />
                  </TableCell>
                  <TableCell>
                    <Input
                      type="number"
                      min={0}
                      step={0.01}
                      value={item.unitCost}
                      onChange={(e) => updateItem(idx, 'unitCost', Number(e.target.value))}
                      className="h-8"
                    />
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    ₨{' '}
                    {(item.quantity * item.unitCost).toLocaleString('en-LK', {
                      minimumFractionDigits: 2,
                    })}
                  </TableCell>
                  <TableCell>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => removeItem(idx)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
            <TableFooter>
              <TableRow>
                <TableCell colSpan={3} className="text-right font-medium">
                  Subtotal
                </TableCell>
                <TableCell className="text-right font-bold">
                  ₨ {subtotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
                </TableCell>
                <TableCell />
              </TableRow>
            </TableFooter>
          </Table>
        </div>
      ) : (
        <div className="rounded-md border border-dashed p-6 text-center">
          <p className="text-sm text-muted-foreground">
            No items added yet. Click &quot;Add Item&quot; to start.
          </p>
        </div>
      )}

      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
