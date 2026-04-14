'use client';

import { type Control, type FieldArrayWithId, type UseFieldArrayRemove } from 'react-hook-form';
import { Trash2 } from 'lucide-react';

import type { AdjustmentFormValues } from '@/lib/validations/adjustment';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface AdjustmentItemsProps {
  control: Control<AdjustmentFormValues>;
  fields: FieldArrayWithId<AdjustmentFormValues, 'items'>[];
  remove: UseFieldArrayRemove;
}

export function AdjustmentItems({ control, fields, remove }: AdjustmentItemsProps) {
  return (
    <div className="space-y-4">
      {fields.map((field, index) => {
        return (
          <div
            key={field.id}
            className="rounded-md border border-gray-200 p-4 dark:border-gray-700"
          >
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
                name={`items.${index}.currentQuantity`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Current Qty</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={0}
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
                name={`items.${index}.newQuantity`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>New Qty</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={0}
                        {...field}
                        onChange={(e) => field.onChange(Number(e.target.value))}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <DifferenceDisplay control={control} index={index} />
            </div>

            <div className="mt-3">
              <FormField
                control={control}
                name={`items.${index}.notes`}
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Item Notes (optional)</FormLabel>
                    <FormControl>
                      <Input placeholder="Notes for this item..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function DifferenceDisplay({
  control,
  index,
}: {
  control: Control<AdjustmentFormValues>;
  index: number;
}) {
  return (
    <FormField
      control={control}
      name={`items.${index}.newQuantity`}
      render={() => (
        <FormItem>
          <FormLabel>Difference</FormLabel>
          <DifferenceValue control={control} index={index} />
        </FormItem>
      )}
    />
  );
}

function DifferenceValue({
  control,
  index,
}: {
  control: Control<AdjustmentFormValues>;
  index: number;
}) {
  // Use watch via FormField to get reactive values
  return (
    <FormField
      control={control}
      name={`items.${index}.currentQuantity`}
      render={({ field: currentField }) => (
        <FormField
          control={control}
          name={`items.${index}.newQuantity`}
          render={({ field: newField }) => {
            const diff = (newField.value ?? 0) - (currentField.value ?? 0);
            return (
              <div
                className={cn(
                  'flex h-10 items-center rounded-md border px-3 text-sm font-semibold',
                  diff > 0
                    ? 'border-green-200 bg-green-50 text-green-700 dark:border-green-800 dark:bg-green-900/20 dark:text-green-400'
                    : diff < 0
                      ? 'border-red-200 bg-red-50 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400'
                      : 'border-gray-200 bg-gray-50 text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400'
                )}
              >
                {diff > 0 ? '+' : ''}
                {diff}
              </div>
            );
          }}
        />
      )}
    />
  );
}
