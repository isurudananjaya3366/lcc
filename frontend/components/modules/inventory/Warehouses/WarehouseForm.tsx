'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { type Resolver } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Loader2 } from 'lucide-react';

import {
  warehouseFormSchema,
  warehouseFormDefaults,
  type WarehouseFormValues,
} from '@/lib/validations/warehouse';
import warehouseService from '@/services/api/warehouseService';
import { inventoryKeys } from '@/lib/queryKeys';

import { Form } from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

import { WarehouseNameInput } from './WarehouseNameInput';
import { WarehouseAddressForm } from './WarehouseAddressForm';
import { WarehouseSettings } from './WarehouseSettings';

interface WarehouseFormProps {
  warehouseId?: string;
}

export function WarehouseForm({ warehouseId }: WarehouseFormProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const isEditing = !!warehouseId;

  const { data: existing, isLoading: loadingExisting } = useQuery({
    queryKey: [...inventoryKeys.all(), 'warehouse', warehouseId],
    queryFn: () => warehouseService.getWarehouseById(warehouseId!),
    enabled: isEditing,
  });

  const form = useForm<WarehouseFormValues>({
    resolver: zodResolver(warehouseFormSchema) as Resolver<WarehouseFormValues>,
    defaultValues: warehouseFormDefaults,
    values: existing?.data
      ? {
          name: existing.data.name,
          code: existing.data.code,
          description: existing.data.description ?? '',
          address: {
            street: existing.data.address.street,
            street2: existing.data.address.street2 ?? '',
            city: existing.data.address.city,
            state: existing.data.address.state,
            postalCode: existing.data.address.postalCode ?? '',
            country: existing.data.address.country || 'LK',
          },
          contactPhone: existing.data.contactPhone ?? '',
          contactEmail: existing.data.contactEmail ?? '',
          capacity: existing.data.capacity,
          isPrimary: existing.data.isPrimary,
          isActive: existing.data.isActive,
        }
      : undefined,
    mode: 'onBlur',
    reValidateMode: 'onChange',
  });

  const createMutation = useMutation({
    mutationFn: (values: WarehouseFormValues) =>
      warehouseService.createWarehouse({
        name: values.name,
        code: values.code,
        description: values.description || undefined,
        address: {
          street: values.address.street,
          street2: values.address.street2 || undefined,
          city: values.address.city,
          state: values.address.state,
          postalCode: values.address.postalCode || '',
          country: values.address.country,
        },
        contactPhone: values.contactPhone || undefined,
        contactEmail: values.contactEmail || undefined,
        capacity: values.capacity,
        isPrimary: values.isPrimary,
        isActive: values.isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
      router.push('/inventory/warehouses');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (values: WarehouseFormValues) =>
      warehouseService.updateWarehouse(warehouseId!, {
        name: values.name,
        code: values.code,
        description: values.description || undefined,
        address: {
          street: values.address.street,
          street2: values.address.street2 || undefined,
          city: values.address.city,
          state: values.address.state,
          postalCode: values.address.postalCode || '',
          country: values.address.country,
        },
        contactPhone: values.contactPhone || undefined,
        contactEmail: values.contactEmail || undefined,
        capacity: values.capacity,
        isPrimary: values.isPrimary,
        isActive: values.isActive,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all() });
      router.push('/inventory/warehouses');
    },
  });

  const mutation = isEditing ? updateMutation : createMutation;

  const handleSubmit = form.handleSubmit(async (data) => {
    await mutation.mutateAsync(data);
  });

  if (isEditing && loadingExisting) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-gray-100">
          {isEditing ? 'Edit Warehouse' : 'New Warehouse'}
        </h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {isEditing ? 'Update warehouse details and settings.' : 'Add a new warehouse location.'}
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Warehouse Details</CardTitle>
            </CardHeader>
            <CardContent>
              <WarehouseNameInput control={form.control} isLoading={mutation.isPending} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Address</CardTitle>
            </CardHeader>
            <CardContent>
              <WarehouseAddressForm control={form.control} isLoading={mutation.isPending} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <WarehouseSettings control={form.control} isLoading={mutation.isPending} />
            </CardContent>
          </Card>

          {mutation.isError && (
            <div className="rounded-md bg-red-50 p-4 text-sm text-red-800 dark:bg-red-900/20 dark:text-red-400">
              Failed to {isEditing ? 'update' : 'create'} warehouse. Please try again.
            </div>
          )}

          <div className="flex items-center justify-end gap-3 border-t border-gray-200 pt-6 dark:border-gray-700">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={mutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {isEditing ? 'Save Changes' : 'Create Warehouse'}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
