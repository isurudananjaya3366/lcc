'use client';

import { useState } from 'react';
import { useFormContext } from 'react-hook-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SelectSavedAddress } from './SelectSavedAddress';
import { AddNewAddress } from './AddNewAddress';
import type { ShippingAddress } from '@/types/storefront/checkout.types';
import type { ShippingStepData } from '@/lib/validations/checkoutSchemas';

type SavedAddress = ShippingAddress & { id: string; name?: string; phone?: string };

interface SavedAddressesProps {
  addresses: SavedAddress[];
  onUseNewAddress: () => void;
}

export const SavedAddresses = ({ addresses, onUseNewAddress }: SavedAddressesProps) => {
  const { setValue } = useFormContext<ShippingStepData>();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = (address: SavedAddress) => {
    setSelectedId(address.id);
    setValue('province', address.province, { shouldValidate: true });
    setValue('district', address.district, { shouldValidate: true });
    setValue('city', address.city, { shouldValidate: true });
    setValue('address1', address.address1, { shouldValidate: true });
    setValue('address2', address.address2 || '', { shouldValidate: false });
    setValue('landmark', address.landmark || '', { shouldValidate: false });
    setValue('postalCode', address.postalCode, { shouldValidate: true });
  };

  if (addresses.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Saved Addresses</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {addresses.map((address) => (
          <SelectSavedAddress
            key={address.id}
            address={address}
            selected={selectedId === address.id}
            onSelect={handleSelect}
          />
        ))}
        <AddNewAddress onClick={onUseNewAddress} />
      </CardContent>
    </Card>
  );
};
