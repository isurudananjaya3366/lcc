'use client';

import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

interface AddressesHeaderProps {
  onAdd: () => void;
}

export function AddressesHeader({ onAdd }: AddressesHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold tracking-tight">Saved Addresses</h2>
        <p className="text-sm text-muted-foreground">
          Manage your shipping and billing addresses
        </p>
      </div>
      <Button onClick={onAdd} className="gap-2">
        <Plus className="h-4 w-4" />
        Add Address
      </Button>
    </div>
  );
}
