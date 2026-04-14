'use client';

import { type Control, type FieldArrayWithId, type UseFieldArrayRemove } from 'react-hook-form';
import { Trash2 } from 'lucide-react';

import type { TransferFormValues } from '@/lib/validations/transfer';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface TransferItemsProps {
  control: Control<TransferFormValues>;
  fields: FieldArrayWithId<TransferFormValues, 'items'>[];
  remove: UseFieldArrayRemove;
}

export function TransferItems({ control, fields, remove }: TransferItemsProps) {
  const totalItems = fields.length;

  return (
    <div className="space-y-4">
      {fields.map((field, index) => (
        <div key={field.id} className="rounded-md border border-gray-200 p-4 dark:border-gray-700">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Item {index + 1}
            </span>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
              onClick={() => remove(index)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <FormField
              control={control}
              name={`items.${index}.productId`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Product ID</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter product ID" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={control}
              name={`items.${index}.availableQuantity`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Available</FormLabel>
                  <div
                    className={cn(
                      'flex h-10 items-center rounded-md border px-3 text-sm',
                      field.value > 100
                        ? 'border-green-200 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : field.value > 10
                          ? 'border-yellow-200 bg-yellow-50 text-yellow-700 dark:border-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                          : field.value > 0
                            ? 'border-orange-200 bg-orange-50 text-orange-700 dark:border-orange-800 dark:bg-orange-900/20 dark:text-orange-400'
                            : 'border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400'
                    )}
                  >
                    {field.value} units
                  </div>
                </FormItem>
              )}
            />

            <FormField
              control={control}
              name={`items.${index}.quantity`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Transfer Qty</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={1}
                      {...field}
                      onChange={(e) => field.onChange(Number(e.target.value))}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={control}
              name={`items.${index}.notes`}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Notes (optional)</FormLabel>
                  <FormControl>
                    <Input placeholder="Item notes..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>
      ))}

      {/* Summary */}
      {totalItems > 0 && (
        <div className="flex items-center justify-between rounded-md bg-gray-50 px-4 py-3 text-sm dark:bg-gray-800">
          <span className="text-gray-600 dark:text-gray-400">
            {totalItems} {totalItems === 1 ? 'product' : 'products'}
          </span>
        </div>
      )}
    </div>
  );
}
