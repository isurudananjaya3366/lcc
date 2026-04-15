'use client';

import { useCallback } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, Plus } from 'lucide-react';

import { adjustmentFormSchema, type AdjustmentFormValues } from '@/lib/validations/adjustment';
import { AdjustmentReason } from '@/types/inventory';
import inventoryService from '@/services/api/inventoryService';
import { inventoryKeys } from '@/lib/queryKeys';

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import { useWarehouses } from '@/hooks/queries/useWarehouses';
import { AdjustmentItems } from './AdjustmentItems';

const reasonOptions: { value: AdjustmentReason; label: string }[] = [
  { value: AdjustmentReason.DAMAGE, label: 'Damage' },
  { value: AdjustmentReason.THEFT, label: 'Theft' },
  { value: AdjustmentReason.EXPIRED, label: 'Expired' },
  { value: AdjustmentReason.RECOUNT, label: 'Recount' },
  { value: AdjustmentReason.ERROR, label: 'Error Correction' },
  { value: AdjustmentReason.OTHER, label: 'Other' },
];

export function AdjustmentForm() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: warehousesData, isLoading: warehousesLoading } = useWarehouses();
  const warehouses = warehousesData?.data ?? [];

  const form = useForm<AdjustmentFormValues>({
    resolver: zodResolver(adjustmentFormSchema),
    defaultValues: {
      warehouseId: '',
      reason: undefined as unknown as AdjustmentReason,
      reasonNotes: '',
      items: [],
    },
    mode: 'onBlur',
    reValidateMode: 'onChange',
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'items',
  });

  const mutation = useMutation({
    mutationFn: async (values: AdjustmentFormValues) => {
      const requests = values.items.map((item) =>
        inventoryService.createStockAdjustment({
          productId: item.productId,
          variantId: item.variantId,
          warehouseId: values.warehouseId,
          quantityChange: item.newQuantity - item.currentQuantity,
          reason: values.reason,
          reasonNotes: values.reasonNotes,
        })
      );
      return Promise.all(requests);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
      router.push('/inventory/adjustments');
    },
  });

  const handleAddItem = useCallback(() => {
    append({
      productId: '',
      variantId: undefined,
      currentQuantity: 0,
      newQuantity: 0,
      notes: '',
    });
  }, [append]);

  const handleSubmit = form.handleSubmit(async (data) => {
    await mutation.mutateAsync(data);
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
          New Stock Adjustment
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Adjust stock quantities for products in a warehouse.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Adjustment Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Adjustment Details</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="warehouseId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Warehouse</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={warehousesLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select warehouse" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {warehouses.map((wh) => (
                          <SelectItem key={wh.id} value={wh.id}>
                            {wh.name} ({wh.code})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="reason"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reason</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select reason" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {reasonOptions.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="sm:col-span-2">
                <FormField
                  control={form.control}
                  name="reasonNotes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Notes (optional)</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Additional notes about this adjustment..."
                          className="resize-none"
                          rows={3}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            </CardContent>
          </Card>

          {/* Items Section */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">Products</CardTitle>
              <Button type="button" variant="outline" size="sm" onClick={handleAddItem}>
                <Plus className="mr-2 h-4 w-4" />
                Add Product
              </Button>
            </CardHeader>
            <CardContent>
              {fields.length === 0 ? (
                <div className="rounded-md border border-dashed border-gray-300 p-8 text-center dark:border-gray-700">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No products added yet. Click &quot;Add Product&quot; to begin.
                  </p>
                </div>
              ) : (
                <AdjustmentItems control={form.control} fields={fields} remove={remove} />
              )}
              {form.formState.errors.items?.message && (
                <p className="mt-2 text-sm text-red-500">{form.formState.errors.items.message}</p>
              )}
            </CardContent>
          </Card>

          {/* Error */}
          {mutation.isError && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
              Failed to create stock adjustment. Please try again.
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 border-t border-gray-200 pt-6 dark:border-gray-700">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={mutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Submit Adjustment
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
