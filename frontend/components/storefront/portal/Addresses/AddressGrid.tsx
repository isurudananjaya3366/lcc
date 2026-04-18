'use client';

import { AddressCard } from './AddressCard';
import { EmptyAddresses } from './EmptyAddresses';
import type { PortalAddress } from '@/types/storefront/portal.types';

interface AddressGridProps {
  addresses: PortalAddress[];
  onEdit: (address: PortalAddress) => void;
  onDelete: (address: PortalAddress) => void;
  onSetDefault: (id: string) => void;
  onAdd: () => void;
}

export function AddressGrid({
  addresses,
  onEdit,
  onDelete,
  onSetDefault,
  onAdd,
}: AddressGridProps) {
  if (addresses.length === 0) {
    return <EmptyAddresses onAdd={onAdd} />;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {addresses.map((address) => (
        <AddressCard
          key={address.id}
          address={address}
          onEdit={onEdit}
          onDelete={onDelete}
          onSetDefault={onSetDefault}
        />
      ))}
    </div>
  );
}
