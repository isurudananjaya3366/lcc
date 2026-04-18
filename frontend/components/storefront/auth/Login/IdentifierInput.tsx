'use client';

import { useFormContext } from 'react-hook-form';
import { Mail, Phone } from 'lucide-react';
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import type { LoginFormValues } from '@/lib/validations/loginSchema';

function detectInputType(value: string): 'email' | 'phone' {
  const trimmed = value.trim();
  if (/^(\+94|0)\d/.test(trimmed) || /^\d{7,}$/.test(trimmed)) return 'phone';
  return 'email';
}

export function IdentifierInput() {
  const form = useFormContext<LoginFormValues>();
  const value = form.watch('identifier') || '';
  const inputType = detectInputType(value);
  const Icon = inputType === 'phone' ? Phone : Mail;

  return (
    <FormField
      control={form.control}
      name="identifier"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Email or Phone</FormLabel>
          <FormControl>
            <div className="relative">
              <Icon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Email or phone number"
                className="pl-10"
                {...field}
              />
            </div>
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
