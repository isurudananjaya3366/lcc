'use client';

import { type Control } from 'react-hook-form';
import type { WarehouseFormValues } from '@/lib/validations/warehouse';
import { FormControl, FormField, FormItem, FormLabel, FormDescription } from '@/components/ui/form';
import { Switch } from '@/components/ui/switch';

interface WarehouseSettingsProps {
  control: Control<WarehouseFormValues>;
  isLoading?: boolean;
}

export function WarehouseSettings({ control, isLoading }: WarehouseSettingsProps) {
  return (
    <div className="space-y-6">
      <FormField
        control={control}
        name="isPrimary"
        render={({ field }) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="space-y-0.5">
              <FormLabel className="text-base">Default Warehouse</FormLabel>
              <FormDescription>
                Set this as the default warehouse for new products and orders.
              </FormDescription>
            </div>
            <FormControl>
              <Switch checked={field.value} onCheckedChange={field.onChange} disabled={isLoading} />
            </FormControl>
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="isActive"
        render={({ field }) => (
          <FormItem className="flex flex-row items-center justify-between rounded-lg border border-gray-200 p-4 dark:border-gray-700">
            <div className="space-y-0.5">
              <FormLabel className="text-base">Active Status</FormLabel>
              <FormDescription>
                Inactive warehouses are hidden from selectors and cannot receive new stock.
              </FormDescription>
            </div>
            <FormControl>
              <Switch checked={field.value} onCheckedChange={field.onChange} disabled={isLoading} />
            </FormControl>
          </FormItem>
        )}
      />
    </div>
  );
}
