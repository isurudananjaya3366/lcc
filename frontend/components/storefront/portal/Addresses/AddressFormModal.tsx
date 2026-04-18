'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { AddressForm } from './AddressForm';
import type { PortalAddress } from '@/types/storefront/portal.types';
import type { AddressFormValues } from '@/lib/validations/addressSchema';

interface AddressFormModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  address?: PortalAddress | null;
  onSave: (data: AddressFormValues) => void;
  isPending: boolean;
}

export function AddressFormModal({
  open,
  onOpenChange,
  address,
  onSave,
  isPending,
}: AddressFormModalProps) {
  const isEditing = !!address;

  const defaultValues: Partial<AddressFormValues> | undefined = address
    ? {
        label: address.label ?? '',
        firstName: address.firstName,
        lastName: address.lastName,
        phone: address.phone ?? '',
        addressLine1: address.addressLine1,
        addressLine2: address.addressLine2 ?? '',
        province: address.province,
        district: address.district,
        city: address.city,
        postalCode: address.postalCode,
        type: address.type,
        isDefault: address.isDefault,
      }
    : undefined;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? 'Edit Address' : 'Add New Address'}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? 'Update the address details below.'
              : 'Fill in the details to add a new address.'}
          </DialogDescription>
        </DialogHeader>
        <AddressForm
          key={address?.id ?? 'new'}
          defaultValues={defaultValues}
          onSubmit={onSave}
          onCancel={() => onOpenChange(false)}
          isPending={isPending}
        />
      </DialogContent>
    </Dialog>
  );
}
