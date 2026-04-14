'use client';

import {
  useFieldArray,
  Control,
  FieldErrors,
  UseFormRegister,
  UseFormWatch,
} from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Plus, Trash2 } from 'lucide-react';
import type { QuoteFormValues } from '@/lib/validations/quote';

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

interface QuoteItemsSectionProps {
  control: Control<QuoteFormValues>;
  register: UseFormRegister<QuoteFormValues>;
  watch: UseFormWatch<QuoteFormValues>;
  errors: FieldErrors<QuoteFormValues>;
}

/**
 * Reusable Quote Items section with add/remove line items.
 * Task 74: Quote Items Section
 */
export function QuoteItemsSection({ control, register, watch, errors }: QuoteItemsSectionProps) {
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const watchItems = watch('items');

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">Quote Items</CardTitle>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() =>
            append({
              productId: '',
              productName: '',
              quantity: 1,
              unitPrice: 0,
              discountPercent: 0,
            })
          }
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Item
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.id} className="grid grid-cols-12 items-end gap-3 rounded-md border p-3">
            <div className="col-span-3">
              <Label>Product Name</Label>
              <Input placeholder="Product name" {...register(`items.${index}.productName`)} />
              {errors.items?.[index]?.productName && (
                <p className="mt-1 text-xs text-red-500">
                  {errors.items[index]?.productName?.message}
                </p>
              )}
            </div>
            <div className="col-span-2">
              <Label>Product ID</Label>
              <Input placeholder="SKU / ID" {...register(`items.${index}.productId`)} />
              {errors.items?.[index]?.productId && (
                <p className="mt-1 text-xs text-red-500">
                  {errors.items[index]?.productId?.message}
                </p>
              )}
            </div>
            <div className="col-span-1">
              <Label>Qty</Label>
              <Input
                type="number"
                min={1}
                {...register(`items.${index}.quantity`, { valueAsNumber: true })}
              />
            </div>
            <div className="col-span-2">
              <Label>Unit Price (₨)</Label>
              <Input
                type="number"
                min={0}
                step="0.01"
                {...register(`items.${index}.unitPrice`, { valueAsNumber: true })}
              />
            </div>
            <div className="col-span-1">
              <Label>Disc %</Label>
              <Input
                type="number"
                min={0}
                max={100}
                {...register(`items.${index}.discountPercent`, { valueAsNumber: true })}
              />
            </div>
            <div className="col-span-2">
              <Label>Line Total</Label>
              <p className="py-2 text-sm font-medium">
                {formatCurrency(
                  (watchItems[index]?.quantity || 0) *
                    (watchItems[index]?.unitPrice || 0) *
                    (1 - (watchItems[index]?.discountPercent || 0) / 100)
                )}
              </p>
            </div>
            <div className="col-span-1">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                disabled={fields.length === 1}
                onClick={() => remove(index)}
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </Button>
            </div>
          </div>
        ))}
        {errors.items?.message && <p className="text-sm text-red-500">{errors.items.message}</p>}
      </CardContent>
    </Card>
  );
}
