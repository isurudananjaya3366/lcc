'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { Package } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { customerKeys } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';

interface OrdersTabProps {
  customerId: string;
}

interface Order {
  id: string;
  orderNumber: string;
  date: string;
  itemCount: number;
  total: number;
  status: string;
}

function getStatusVariant(status: string) {
  switch (status.toLowerCase()) {
    case 'paid':
      return 'default';
    case 'processing':
      return 'processing';
    case 'pending':
      return 'pending';
    case 'cancelled':
      return 'cancelled';
    default:
      return 'outline';
  }
}

function formatLKR(amount: number): string {
  return `₨${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function OrdersTab({ customerId }: OrdersTabProps) {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: [...customerKeys.orders(customerId), { page }],
    queryFn: () => customerService.getCustomerTransactions(customerId, {}),
    enabled: !!customerId,
  });

  const orders: Order[] = (data?.data ?? []).map((t) => ({
    id: t.id,
    orderNumber: t.referenceId ?? t.id.slice(0, 8),
    date: t.transactionDate,
    itemCount: 0,
    total: t.amount,
    status: t.transactionType === 'SALE' ? 'Paid' : t.transactionType,
  }));

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Package className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium">No Orders Yet</h3>
        <p className="text-sm text-muted-foreground mb-4">
          This customer hasn&apos;t placed any orders.
        </p>
        <Button asChild>
          <Link href="/orders/new">Create Order</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">
          Order History
          <Badge variant="secondary" className="ml-2">
            {orders.length}
          </Badge>
        </h3>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[120px]">Order #</TableHead>
            <TableHead className="w-[100px]">Date</TableHead>
            <TableHead className="w-[80px] text-center">Items</TableHead>
            <TableHead className="w-[120px] text-right">Total</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {orders.map((order) => (
            <TableRow key={order.id}>
              <TableCell>
                <Link
                  href={`/orders/${order.id}`}
                  className="text-primary hover:underline font-medium"
                >
                  {order.orderNumber}
                </Link>
              </TableCell>
              <TableCell className="text-sm">
                {new Date(order.date).toLocaleDateString('en-LK', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}
              </TableCell>
              <TableCell className="text-center">{order.itemCount}</TableCell>
              <TableCell className="text-right font-medium">{formatLKR(order.total)}</TableCell>
              <TableCell>
                <Badge
                  variant={
                    getStatusVariant(order.status) as
                      | 'default'
                      | 'secondary'
                      | 'destructive'
                      | 'outline'
                  }
                >
                  {order.status}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {data && data.pagination && data.pagination.totalPages > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {data.pagination.totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={!data.pagination.hasNext}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

export { OrdersTab as OrderHistoryTable };
