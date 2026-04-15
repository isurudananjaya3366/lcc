'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent } from '@/components/ui/card';
import { customerFormSchema, type CustomerFormValues } from '@/lib/validations/customer';
import { useCreateCustomer } from '@/hooks/crm/useCustomers';
import { CustomerContactFields } from './CustomerContactFields';
import { CustomerAddressFields } from './CustomerAddressFields';
import type { CustomerType, PaymentTerms } from '@/types/customer';

export function CustomerForm() {
  const router = useRouter();
  const createCustomer = useCreateCustomer();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<CustomerFormValues>({
    resolver: zodResolver(customerFormSchema),
    defaultValues: {
      customerType: 'INDIVIDUAL',
      addressCountry: 'Sri Lanka',
    },
    mode: 'onChange',
  });

  const customerType = watch('customerType');
  const paymentTerms = watch('paymentTerms');

  function onSubmit(values: CustomerFormValues) {
    createCustomer.mutate(
      {
        customerType: values.customerType as CustomerType,
        firstName: values.firstName || undefined,
        lastName: values.lastName || undefined,
        companyName: values.companyName || undefined,
        displayName: values.displayName,
        email: values.email || undefined,
        phone: values.phone || undefined,
        mobile: values.mobile || undefined,
        taxId: values.taxId || undefined,
        addresses: values.addressStreet
          ? [
              {
                addressType: 'BOTH' as const,
                street: values.addressStreet,
                city: values.addressCity || '',
                state: values.addressState || '',
                postalCode: values.addressPostalCode || '',
                country: values.addressCountry || 'Sri Lanka',
                isDefault: true,
              },
            ]
          : undefined,
        creditLimit: values.creditLimit
          ? {
              creditLimit: values.creditLimit,
              paymentTerms: (values.paymentTerms as PaymentTerms) || undefined,
            }
          : undefined,
      },
      {
        onSuccess: () => router.push('/customers'),
      }
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/customers">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Create New Customer</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardContent className="p-6 space-y-6">
            {/* Customer Type */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Customer Type</h3>
              <Select
                value={customerType}
                onValueChange={(v) =>
                  setValue('customerType', v as CustomerFormValues['customerType'])
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="INDIVIDUAL">Individual</SelectItem>
                  <SelectItem value="BUSINESS">Business</SelectItem>
                  <SelectItem value="WHOLESALER">Wholesaler</SelectItem>
                  <SelectItem value="DISTRIBUTOR">Distributor</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Personal / Company Information */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">
                {customerType === 'INDIVIDUAL' ? 'Personal Information' : 'Company Information'}
              </h3>

              {customerType === 'INDIVIDUAL' ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name *</Label>
                    <Input id="firstName" {...register('firstName')} />
                    {errors.firstName && (
                      <p className="text-xs text-destructive">{errors.firstName.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name</Label>
                    <Input id="lastName" {...register('lastName')} />
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <Label htmlFor="companyName">Company Name *</Label>
                  <Input id="companyName" {...register('companyName')} />
                  {errors.companyName && (
                    <p className="text-xs text-destructive">{errors.companyName.message}</p>
                  )}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="displayName">Display Name *</Label>
                <Input id="displayName" {...register('displayName')} />
                {errors.displayName && (
                  <p className="text-xs text-destructive">{errors.displayName.message}</p>
                )}
              </div>
            </div>

            <Separator />

            {/* Contact Details */}
            <CustomerContactFields register={register} errors={errors} />

            <Separator />

            {/* Address */}
            <CustomerAddressFields register={register} errors={errors} />

            <Separator />

            {/* Credit & Payment Terms */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Credit &amp; Payment Terms</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="creditLimit">Credit Limit (₨)</Label>
                  <Input
                    id="creditLimit"
                    type="number"
                    min={0}
                    {...register('creditLimit', { valueAsNumber: true })}
                  />
                  {errors.creditLimit && (
                    <p className="text-xs text-destructive">{errors.creditLimit.message}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <Label>Payment Terms</Label>
                  <Select
                    value={paymentTerms || ''}
                    onValueChange={(v) =>
                      setValue('paymentTerms', v as CustomerFormValues['paymentTerms'])
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select terms" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="NET_0">Net 0 (Due on receipt)</SelectItem>
                      <SelectItem value="NET_15">Net 15</SelectItem>
                      <SelectItem value="NET_30">Net 30</SelectItem>
                      <SelectItem value="NET_45">Net 45</SelectItem>
                      <SelectItem value="NET_60">Net 60</SelectItem>
                      <SelectItem value="COD">Cash on Delivery</SelectItem>
                      <SelectItem value="PREPAID">Prepaid</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <Separator />

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                {...register('notes')}
                placeholder="Additional notes about this customer..."
                rows={3}
              />
              {errors.notes && <p className="text-xs text-destructive">{errors.notes.message}</p>}
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-3 mt-6">
          <Button type="button" variant="outline" asChild>
            <Link href="/customers">Cancel</Link>
          </Button>
          <Button type="submit" disabled={isSubmitting || createCustomer.isPending}>
            {createCustomer.isPending ? 'Creating...' : 'Create Customer'}
          </Button>
        </div>
      </form>
    </div>
  );
}
