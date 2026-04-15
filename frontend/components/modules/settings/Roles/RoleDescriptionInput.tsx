'use client';

import { UseFormReturn } from 'react-hook-form';
import { Textarea } from '@/components/ui/textarea';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import type { RoleFormValues } from '@/lib/validations/role';

interface RoleDescriptionInputProps {
  form: UseFormReturn<RoleFormValues>;
}

export function RoleDescriptionInput({ form }: RoleDescriptionInputProps) {
  const value = form.watch('description') ?? '';

  return (
    <FormField
      control={form.control}
      name="description"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Description</FormLabel>
          <FormControl>
            <Textarea
              placeholder="Describe this role..."
              rows={3}
              maxLength={200}
              {...field}
              value={field.value ?? ''}
            />
          </FormControl>
          <div className="flex justify-between">
            <FormMessage />
            <span className="text-xs text-muted-foreground">{value.length}/200</span>
          </div>
        </FormItem>
      )}
    />
  );
}
