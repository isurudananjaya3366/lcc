'use client';

import { type Control } from 'react-hook-form';
import type { WarehouseFormValues } from '@/lib/validations/warehouse';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  FormDescription,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';

interface WarehouseNameInputProps {
  control: Control<WarehouseFormValues>;
  isLoading?: boolean;
}

export function WarehouseNameInput({ control, isLoading }: WarehouseNameInputProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <FormField
        control={control}
        name="name"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Warehouse Name</FormLabel>
            <FormControl>
              <Input placeholder="e.g. Main Warehouse" disabled={isLoading} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="code"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Code</FormLabel>
            <FormControl>
              <Input
                placeholder="e.g. WH-MAIN"
                disabled={isLoading}
                {...field}
                onChange={(e) => field.onChange(e.target.value.toUpperCase())}
              />
            </FormControl>
            <FormDescription>Unique uppercase code for this warehouse</FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="sm:col-span-2">
        <FormField
          control={control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description (optional)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Description of this warehouse..."
                  className="resize-none"
                  rows={3}
                  disabled={isLoading}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={control}
        name="contactPhone"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Contact Phone (optional)</FormLabel>
            <FormControl>
              <Input placeholder="+94 XX XXX XXXX" disabled={isLoading} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={control}
        name="contactEmail"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Contact Email (optional)</FormLabel>
            <FormControl>
              <Input
                type="email"
                placeholder="warehouse@example.com"
                disabled={isLoading}
                {...field}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
