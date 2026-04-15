'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent } from '@/components/ui/card';
import { vendorFormSchema, type VendorFormValues } from '@/lib/validations/vendor';
import { useCreateVendor } from '@/hooks/crm/useVendors';
import { VendorContactFields } from './VendorContactFields';
import { VendorTermsFields } from './VendorTermsFields';
import type { VendorType, VendorCategory } from '@/types/vendor';

export function VendorForm() {
  const router = useRouter();
  const createVendor = useCreateVendor();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isValid },
  } = useForm<VendorFormValues>({
    resolver: zodResolver(vendorFormSchema),
    defaultValues: {
      currency: 'LKR',
    },
    mode: 'onChange',
  });

  const vendorType = watch('vendorType');
  const category = watch('category');

  function onSubmit(values: VendorFormValues) {
    createVendor.mutate(
      {
        companyName: values.companyName,
        vendorType: values.vendorType as VendorType,
        category: values.category as VendorCategory,
        phone: values.phone,
        email: values.email,
        website: values.website || undefined,
        paymentTerms: values.paymentTerms as
          | import('@/types/vendor').VendorPaymentTerms
          | undefined,
        currency: values.currency,
        contacts: [
          {
            firstName: values.contactName.split(' ')[0] ?? values.contactName,
            lastName: values.contactName.split(' ').slice(1).join(' ') || '',
            phone: values.phone,
            email: values.email,
            isPrimary: true,
            isAccounts: false,
            isProcurement: false,
          },
        ],
        addresses: values.address
          ? [
              {
                addressType: 'OFFICE' as const,
                street: values.address,
                city: values.city || '',
                state: '',
                postalCode: values.postalCode || '',
                country: 'Sri Lanka',
                isDefault: true,
              },
            ]
          : undefined,
      },
      {
        onSuccess: () => router.push('/vendors'),
      }
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/vendors">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h1 className="text-2xl font-bold tracking-tight">Add New Vendor</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardContent className="p-6 space-y-6">
            {/* Company Information */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Company Information</h3>
              <div className="space-y-2">
                <Label htmlFor="companyName">Company Name *</Label>
                <Input id="companyName" {...register('companyName')} />
                {errors.companyName && (
                  <p className="text-xs text-destructive">{errors.companyName.message}</p>
                )}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Vendor Type *</Label>
                  <Select
                    value={vendorType || ''}
                    onValueChange={(v) =>
                      setValue('vendorType', v as VendorFormValues['vendorType'])
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="SUPPLIER">Supplier</SelectItem>
                      <SelectItem value="MANUFACTURER">Manufacturer</SelectItem>
                      <SelectItem value="DISTRIBUTOR">Distributor</SelectItem>
                      <SelectItem value="SERVICE_PROVIDER">Service Provider</SelectItem>
                      <SelectItem value="CONTRACTOR">Contractor</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Category *</Label>
                  <Select
                    value={category || ''}
                    onValueChange={(v) => setValue('category', v as VendorFormValues['category'])}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="RAW_MATERIALS">Raw Materials</SelectItem>
                      <SelectItem value="FINISHED_GOODS">Finished Goods</SelectItem>
                      <SelectItem value="SERVICES">Services</SelectItem>
                      <SelectItem value="EQUIPMENT">Equipment</SelectItem>
                      <SelectItem value="UTILITIES">Utilities</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <Separator />

            {/* Contact Details */}
            <VendorContactFields register={register} errors={errors} />

            <Separator />

            {/* Address */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">Address</h3>
              <div className="space-y-2">
                <Label htmlFor="address">Street Address</Label>
                <Input id="address" {...register('address')} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="city">City</Label>
                  <Input id="city" {...register('city')} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="postalCode">Postal Code</Label>
                  <Input id="postalCode" {...register('postalCode')} />
                </div>
              </div>
            </div>

            <Separator />

            {/* Payment Terms */}
            <VendorTermsFields
              register={register}
              errors={errors}
              setValue={setValue}
              watch={watch}
            />

            <Separator />

            <div className="flex items-center justify-end gap-3">
              <Button type="button" variant="outline" asChild>
                <Link href="/vendors">Cancel</Link>
              </Button>
              <Button type="submit" disabled={!isValid || createVendor.isPending}>
                {createVendor.isPending ? 'Creating...' : 'Create Vendor'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
