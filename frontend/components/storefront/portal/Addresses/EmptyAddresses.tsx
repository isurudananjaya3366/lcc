'use client';

import { Button } from '@/components/ui/button';
import { MapPin, Plus } from 'lucide-react';

interface EmptyAddressesProps {
  onAdd: () => void;
}

export function EmptyAddresses({ onAdd }: EmptyAddressesProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <MapPin className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold mb-1">No addresses yet</h3>
      <p className="text-muted-foreground mb-6">
        Add your first address to get started
      </p>
      <Button onClick={onAdd}>
        <Plus className="h-4 w-4 mr-2" />
        Add Address
      </Button>
    </div>
  );
}
