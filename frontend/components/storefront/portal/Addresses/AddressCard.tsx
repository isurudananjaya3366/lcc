'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Pencil, Trash2, Star, Phone } from 'lucide-react';
import type { PortalAddress } from '@/types/storefront/portal.types';

interface AddressCardProps {
  address: PortalAddress;
  onEdit: (address: PortalAddress) => void;
  onDelete: (address: PortalAddress) => void;
  onSetDefault: (id: string) => void;
}

export function AddressCard({
  address,
  onEdit,
  onDelete,
  onSetDefault,
}: AddressCardProps) {
  return (
    <Card className="relative">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            {address.isDefault && (
              <Badge variant="default" className="text-xs">
                Default
              </Badge>
            )}
            <Badge variant="outline" className="text-xs capitalize">
              {address.type}
            </Badge>
            {address.label && (
              <span className="text-sm font-medium text-muted-foreground">
                {address.label}
              </span>
            )}
          </div>
          <div className="flex items-center gap-1">
            {!address.isDefault && (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => onSetDefault(address.id)}
                title="Set as default"
              >
                <Star className="h-4 w-4" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(address)}
              title="Edit address"
            >
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:text-destructive"
              onClick={() => onDelete(address)}
              title="Delete address"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="space-y-1 text-sm">
          <p className="font-medium">
            {address.firstName} {address.lastName}
          </p>
          <p className="text-muted-foreground">{address.addressLine1}</p>
          {address.addressLine2 && (
            <p className="text-muted-foreground">{address.addressLine2}</p>
          )}
          <p className="text-muted-foreground">
            {address.city}, {address.district}
          </p>
          <p className="text-muted-foreground">
            {address.province}, {address.postalCode}
          </p>
          {address.phone && (
            <p className="text-muted-foreground flex items-center gap-1 pt-1">
              <Phone className="h-3 w-3" />
              {address.phone}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
