'use client';

import { useCallback } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Loader2, Plus } from 'lucide-react';

import { transferFormSchema, type TransferFormValues } from '@/lib/validations/transfer';
import { inventoryService } from '@/services/api';
import { inventoryKeys } from '@/lib/queryKeys';
import { useWarehouses } from '@/hooks/queries/useWarehouses';

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

import { TransferItems } from './TransferItems';

export function TransferForm() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: warehousesData, isLoading: warehousesLoading } = useWarehouses();
  const warehouses = warehousesData?.results ?? [];

  const form = useForm<TransferFormValues>({
    resolver: zodResolver(transferFormSchema),
    defaultValues: {
      sourceWarehouseId: '',
      destinationWarehouseId: '',
      expectedDate: '',
      notes: '',
      items: [],
    },
    mode: 'onBlur',
    reValidateMode: 'onChange',
  });

  const sourceWarehouseId = form.watch('sourceWarehouseId');
  const destinationWarehouseId = form.watch('destinationWarehouseId');

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'items',
  });

  const mutation = useMutation({
    mutationFn: (values: TransferFormValues) =>
      inventoryService.createStockTransfer({
        sourceWarehouseId: values.sourceWarehouseId,
        destinationWarehouseId: values.destinationWarehouseId,
        items: values.items.map((item) => ({
          productId: item.productId,
          variantId: item.variantId,
          quantity: item.quantity,
        })),
        requestedDate: values.expectedDate || undefined,
        notes: values.notes || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
      router.push('/inventory/transfers');
    },
  });

  const handleAddItem = useCallback(() => {
    append({
      productId: '',
      variantId: undefined,
      availableQuantity: 0,
      quantity: 1,
      notes: '',
    });
  }, [append]);

  const handleSubmit = form.handleSubmit(async (data) => {
    await mutation.mutateAsync(data);
  });

  // Filter warehouses for source/destination to exclude the other
  const sourceWarehouses = warehouses.filter(
    (wh) => wh.id !== destinationWarehouseId && wh.isActive
  );
  const destinationWarehouses = warehouses.filter(
    (wh) => wh.id !== sourceWarehouseId && wh.isActive
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
          New Stock Transfer
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Transfer stock between warehouses.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Warehouse Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Warehouses</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="sourceWarehouseId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Source Warehouse</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={warehousesLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select source" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {sourceWarehouses.map((wh) => (
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
                name="destinationWarehouseId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Destination Warehouse</FormLabel>
                    <Select
                      onValueChange={field.onChange}
                      value={field.value}
                      disabled={warehousesLoading}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select destination" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {destinationWarehouses.map((wh) => (
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
                name="expectedDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Expected Date (optional)</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="sm:col-span-2">
                <FormField
                  control={form.control}
                  name="notes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Notes (optional)</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Transfer notes..."
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

          {/* Transfer Items */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">Transfer Items</CardTitle>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddItem}
                disabled={!sourceWarehouseId}
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Item
              </Button>
            </CardHeader>
            <CardContent>
              {!sourceWarehouseId ? (
                <div className="rounded-md border border-dashed border-gray-300 p-8 text-center dark:border-gray-700">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Select a source warehouse to add items.
                  </p>
                </div>
              ) : fields.length === 0 ? (
                <div className="rounded-md border border-dashed border-gray-300 p-8 text-center dark:border-gray-700">
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No items added yet. Click &quot;Add Item&quot; to begin.
                  </p>
                </div>
              ) : (
                <TransferItems control={form.control} fields={fields} remove={remove} />
              )}
              {form.formState.errors.items?.message && (
                <p className="mt-2 text-sm text-red-500">{form.formState.errors.items.message}</p>
              )}
            </CardContent>
          </Card>

          {/* Error */}
          {mutation.isError && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
              Failed to create transfer. Please try again.
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
              Create Transfer
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
