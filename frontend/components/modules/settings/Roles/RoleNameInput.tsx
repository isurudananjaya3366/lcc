'use client';

import { UseFormReturn } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import type { RoleFormValues } from '@/lib/validations/role';

interface RoleNameInputProps {
  form: UseFormReturn<RoleFormValues>;
}

export function RoleNameInput({ form }: RoleNameInputProps) {
  return (
    <FormField
      control={form.control}
      name="name"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Role Name *</FormLabel>
          <FormControl>
            <Input placeholder="Enter role name" {...field} />
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
