'use client';

import { MapPin } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PortalAddress } from '@/types/storefront/portal.types';

interface ShippingAddressCardProps {
  address: PortalAddress;
}

export function ShippingAddressCard({ address }: ShippingAddressCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <MapPin className="h-4 w-4" />
          Shipping Address
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-1 text-sm">
        <p className="font-medium">
          {address.firstName} {address.lastName}
        </p>
        <p>{address.addressLine1}</p>
        {address.addressLine2 && <p>{address.addressLine2}</p>}
        <p>
          {address.city}, {address.district}
        </p>
        <p>
          {address.province}, {address.postalCode}
        </p>
        {address.phone && (
          <p className="pt-1 text-muted-foreground">{address.phone}</p>
        )}
      </CardContent>
    </Card>
  );
}
