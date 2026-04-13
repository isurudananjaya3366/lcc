'use client';

import * as React from 'react';

import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';

export interface PhoneInputProps {
  value?: string;
  onChange?: (value: string) => void;
  countryCode?: string;
  autoFormat?: boolean;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

function formatPhone(value: string): string {
  const digits = value.replace(/\D/g, '');
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
  return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
}

function PhoneInput({
  value = '',
  onChange,
  countryCode = '+94',
  autoFormat = true,
  disabled = false,
  placeholder = '7X XXX XXXX',
  className,
}: PhoneInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value.replace(/\D/g, '').slice(0, 10);
    onChange?.(raw);
  };

  const displayValue = autoFormat ? formatPhone(value) : value;

  return (
    <Input
      type="tel"
      value={displayValue}
      onChange={handleChange}
      disabled={disabled}
      placeholder={placeholder}
      addonBefore={countryCode}
      className={cn(className)}
      maxLength={12}
      aria-label="Phone number"
    />
  );
}

export { PhoneInput };
