'use client';

import { useRouter } from 'next/navigation';
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { poTableColumns } from './POTableColumns';
import type { PurchaseOrder } from '@/types/vendor';

interface POTableProps {
  orders: PurchaseOrder[];
  isLoading: boolean;
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  sortBy: string;
  sortDir: 'asc' | 'desc';
  onSort: (key: string) => void;
}

export function POTable({
  orders,
  isLoading,
  page,
  totalPages,
  onPageChange,
  sortBy,
  sortDir,
  onSort,
}: POTableProps) {
  const router = useRouter();

  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground">No purchase orders found</p>
        <p className="text-sm text-muted-foreground mt-1">
          Create your first purchase order to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {poTableColumns.map((col) => (
                <TableHead key={col.key}>
                  {col.sortable ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="-ml-3 h-8"
                      onClick={() => onSort(col.key)}
                    >
                      {col.label}
                      <ArrowUpDown className="ml-1 h-3 w-3" />
                    </Button>
                  ) : (
                    col.label
                  )}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders.map((po) => (
              <TableRow
                key={po.id}
                className="cursor-pointer"
                onClick={() => router.push(`/purchase-orders/${po.id}`)}
              >
                {poTableColumns.map((col) => (
                  <TableCell
                    key={col.key}
                    onClick={col.key === 'actions' ? (e) => e.stopPropagation() : undefined}
                  >
                    {col.render(po)}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
