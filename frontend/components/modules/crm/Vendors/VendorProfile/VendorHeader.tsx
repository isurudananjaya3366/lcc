'use client';

import { ArrowLeft, Edit, MoreVertical, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Separator } from '@/components/ui/separator';
import type { Vendor } from '@/types/vendor';

interface VendorHeaderProps {
  vendor: Vendor;
  onEdit?: () => void;
  onDelete?: () => void;
}

function getStatusVariant(status: string) {
  switch (status) {
    case 'ACTIVE':
      return 'default';
    case 'INACTIVE':
      return 'secondary';
    case 'SUSPENDED':
      return 'pending';
    case 'BLOCKED':
      return 'destructive';
    default:
      return 'outline';
  }
}

export function VendorHeader({ vendor, onEdit, onDelete }: VendorHeaderProps) {
  const primaryContact = vendor.contacts?.find((c) => c.isPrimary);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/vendors">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <span className="text-sm text-muted-foreground">Back to Vendors</span>
      </div>

      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">{vendor.companyName}</h1>
            <Badge
              variant={
                getStatusVariant(vendor.status) as
                  | 'default'
                  | 'secondary'
                  | 'destructive'
                  | 'outline'
              }
            >
              {vendor.status}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            {vendor.vendorNumber} · {vendor.vendorType.replace(/_/g, ' ')}
          </p>
          {primaryContact && (
            <p className="text-sm text-muted-foreground">
              Contact: {primaryContact.firstName} {primaryContact.lastName}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={onEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem className="text-destructive" onClick={onDelete}>
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Vendor
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <Separator />
    </div>
  );
}
