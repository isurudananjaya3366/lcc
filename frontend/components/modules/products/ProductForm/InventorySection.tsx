'use client';

import { type Control, type UseFormWatch } from 'react-hook-form';
import { Info, Package } from 'lucide-react';

import type { ProductFormData } from '@/lib/validations/product';
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

interface InventorySectionProps {
  control: Control<ProductFormData>;
  isLoading?: boolean;
  watch: UseFormWatch<ProductFormData>;
}

export function InventorySection({ control, isLoading = false, watch }: InventorySectionProps) {
  const trackInventory = watch('track_inventory');
  const initialStock = watch('initial_stock') ?? 0;
  const reorderPoint = watch('reorder_point') ?? 0;

  const getStockStatus = () => {
    if (initialStock === 0) return { label: 'No Stock', color: 'text-gray-500' };
    if (initialStock <= reorderPoint)
      return { label: 'Below Reorder', color: 'text-red-600 dark:text-red-400' };
    if (initialStock <= reorderPoint * 1.5)
      return { label: 'Approaching Reorder', color: 'text-amber-600 dark:text-amber-400' };
    return { label: 'Healthy', color: 'text-green-600 dark:text-green-400' };
  };

  const status = getStockStatus();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Inventory Management</CardTitle>
        <CardDescription>Configure stock tracking and levels</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Track Inventory Toggle */}
        <FormField
          control={control}
          name="track_inventory"
          render={({ field }) => (
            <FormItem className="flex items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
              <div className="space-y-0.5">
                <FormLabel className="text-base">Track Inventory</FormLabel>
                <FormDescription>Enable to manage stock levels for this product</FormDescription>
              </div>
              <FormControl>
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                  disabled={isLoading}
                />
              </FormControl>
            </FormItem>
          )}
        />

        {/* Info Alert */}
        <div className="flex items-start gap-2 rounded-lg bg-blue-50 p-3 text-sm text-blue-800 dark:bg-blue-950/30 dark:text-blue-300">
          <Info className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            {trackInventory
              ? 'Stock levels will be automatically adjusted with sales and purchases.'
              : 'This product will not affect inventory counts.'}
          </span>
        </div>

        {/* Conditional Stock Fields */}
        {trackInventory && (
          <div className="space-y-4 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="grid gap-4 sm:grid-cols-2">
              {/* Initial Stock */}
              <FormField
                control={control}
                name="initial_stock"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Initial Stock Quantity</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        inputMode="numeric"
                        min={0}
                        step={1}
                        placeholder="0"
                        disabled={isLoading}
                        value={field.value ?? ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          field.onChange(val === '' ? undefined : parseInt(val, 10));
                        }}
                        onBlur={field.onBlur}
                      />
                    </FormControl>
                    <FormDescription>Starting inventory quantity</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Reorder Point */}
              <FormField
                control={control}
                name="reorder_point"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reorder Point</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        inputMode="numeric"
                        min={0}
                        step={1}
                        placeholder="0"
                        disabled={isLoading}
                        value={field.value ?? ''}
                        onChange={(e) => {
                          const val = e.target.value;
                          field.onChange(val === '' ? undefined : parseInt(val, 10));
                        }}
                        onBlur={field.onBlur}
                      />
                    </FormControl>
                    <FormDescription>Alert when stock falls below this level</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* Stock Status */}
            {initialStock > 0 && (
              <div className="flex items-center gap-2 rounded-lg bg-gray-50 p-3 dark:bg-gray-800/50">
                <Package className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Current Stock: <span className="font-medium">{initialStock} units</span>
                </span>
                <span className="mx-2 text-gray-300 dark:text-gray-600">|</span>
                <span className={`text-sm font-medium ${status.color}`}>{status.label}</span>
              </div>
            )}

            {/* Reorder Point Warning */}
            {reorderPoint > 0 && reorderPoint > initialStock && (
              <p className="text-xs text-amber-600 dark:text-amber-400">
                Reorder point is higher than initial stock — you may receive an immediate low stock
                alert.
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
