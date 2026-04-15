'use client';

import { Badge } from '@/components/ui/badge';
import type { Vendor } from '@/types/vendor';
import type { ColumnDef } from '@tanstack/react-table';
import { VendorActionsCell } from './VendorActionsCell';

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

export const vendorTableColumns: ColumnDef<Vendor>[] = [
  {
    accessorKey: 'companyName',
    header: 'Name',
    size: 200,
    cell: ({ row }) => (
      <div>
        <p className="font-medium">{row.original.companyName}</p>
        <p className="text-xs text-muted-foreground">{row.original.vendorNumber}</p>
      </div>
    ),
  },
  {
    id: 'contact',
    header: 'Contact',
    size: 140,
    cell: ({ row }) => {
      const primary = row.original.contacts?.find((c) => c.isPrimary);
      return (
        <div className="text-sm">
          {primary ? (
            <>
              <p>
                {primary.firstName} {primary.lastName}
              </p>
              <p className="text-xs text-muted-foreground">{primary.phone || primary.email}</p>
            </>
          ) : (
            <span className="text-muted-foreground">{row.original.phone || 'N/A'}</span>
          )}
        </div>
      );
    },
  },
  {
    accessorKey: 'category',
    header: 'Category',
    size: 120,
    cell: ({ row }) => <span className="text-sm">{row.original.category.replace(/_/g, ' ')}</span>,
  },
  {
    accessorKey: 'totalPurchases',
    header: 'Total Purchases',
    size: 120,
    cell: ({ row }) => (
      <span className="text-sm font-medium text-right block">
        ₨{row.original.totalPurchases.toLocaleString('en-LK', { minimumFractionDigits: 0 })}
      </span>
    ),
  },
  {
    accessorKey: 'status',
    header: 'Status',
    size: 100,
    cell: ({ row }) => (
      <Badge
        variant={
          getStatusVariant(row.original.status) as
            | 'default'
            | 'secondary'
            | 'destructive'
            | 'outline'
        }
      >
        {row.original.status}
      </Badge>
    ),
  },
  {
    id: 'actions',
    header: '',
    size: 80,
    cell: ({ row }) => <VendorActionsCell vendor={row.original} />,
  },
];
