'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { UseFormRegister, FieldErrors, UseFormSetValue, UseFormWatch } from 'react-hook-form';
import type { VendorFormValues } from '@/lib/validations/vendor';

interface VendorTermsFieldsProps {
  register: UseFormRegister<VendorFormValues>;
  errors: FieldErrors<VendorFormValues>;
  setValue: UseFormSetValue<VendorFormValues>;
  watch: UseFormWatch<VendorFormValues>;
}

export function VendorTermsFields({ register, errors, setValue, watch }: VendorTermsFieldsProps) {
  const paymentTerms = watch('paymentTerms');
  const currency = watch('currency');

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Payment & Ordering Terms</h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Payment Terms</Label>
          <Select
            value={paymentTerms || ''}
            onValueChange={(v) => setValue('paymentTerms', v as VendorFormValues['paymentTerms'])}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select terms" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="NET_7">Net 7 Days</SelectItem>
              <SelectItem value="NET_15">Net 15 Days</SelectItem>
              <SelectItem value="NET_30">Net 30 Days</SelectItem>
              <SelectItem value="NET_45">Net 45 Days</SelectItem>
              <SelectItem value="NET_60">Net 60 Days</SelectItem>
              <SelectItem value="NET_90">Net 90 Days</SelectItem>
              <SelectItem value="COD">Cash on Delivery</SelectItem>
              <SelectItem value="PREPAID">Prepaid</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label>Currency</Label>
          <Select
            value={currency || 'LKR'}
            onValueChange={(v) => setValue('currency', v as 'LKR' | 'USD')}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="LKR">LKR (Sri Lankan Rupee)</SelectItem>
              <SelectItem value="USD">USD (US Dollar)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="leadTime">Lead Time (days)</Label>
          <Input id="leadTime" type="number" min="0" {...register('leadTime')} />
          {errors.leadTime && <p className="text-xs text-destructive">{errors.leadTime.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="minOrderAmount">Minimum Order (₨)</Label>
          <Input
            id="minOrderAmount"
            type="number"
            min="0"
            step="100"
            {...register('minOrderAmount')}
          />
          {errors.minOrderAmount && (
            <p className="text-xs text-destructive">{errors.minOrderAmount.message}</p>
          )}
        </div>
      </div>
    </div>
  );
}
