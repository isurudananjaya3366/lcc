'use client';

import Link from 'next/link';
import { FileBox } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useVendorPOs } from '@/hooks/crm/useVendors';

interface POHistoryTabProps {
  vendorId: string;
}

function getStatusVariant(status: string) {
  switch (status) {
    case 'RECEIVED':
      return 'default';
    case 'SHIPPED':
      return 'processing';
    case 'ACKNOWLEDGED':
      return 'confirmed';
    case 'SENT':
      return 'pending';
    case 'DRAFT':
      return 'secondary';
    case 'CANCELLED':
      return 'cancelled';
    default:
      return 'outline';
  }
}

export function POHistoryTab({ vendorId }: POHistoryTabProps) {
  const { data, isLoading } = useVendorPOs(vendorId);
  const pos = data?.data ?? [];

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (pos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileBox className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium">No Purchase Orders</h3>
        <p className="text-sm text-muted-foreground">
          No purchase orders have been created for this vendor.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">
        Purchase Orders
        <Badge variant="secondary" className="ml-2">
          {pos.length}
        </Badge>
      </h3>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>PO #</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-center">Items</TableHead>
            <TableHead className="text-right">Total</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {pos.map((po) => (
            <TableRow key={po.id}>
              <TableCell>
                <Link
                  href={`/purchase-orders/${po.id}`}
                  className="text-primary hover:underline font-medium"
                >
                  {po.poNumber}
                </Link>
              </TableCell>
              <TableCell className="text-sm">
                {new Date(po.orderDate).toLocaleDateString('en-LK', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </TableCell>
              <TableCell className="text-center">{po.items.length}</TableCell>
              <TableCell className="text-right font-medium">
                ₨{po.total.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
              </TableCell>
              <TableCell>
                <Badge
                  variant={
                    getStatusVariant(po.status) as
                      | 'default'
                      | 'secondary'
                      | 'destructive'
                      | 'outline'
                  }
                >
                  {po.status}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
