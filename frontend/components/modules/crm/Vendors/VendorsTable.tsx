'use client';

import { useRouter } from 'next/navigation';
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { vendorTableColumns } from './VendorTableColumns';
import type { Vendor } from '@/types/vendor';

interface VendorsTableProps {
  vendors: Vendor[];
  isLoading?: boolean;
  page: number;
  pageSize: number;
  totalPages: number;
  totalCount: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  onSortChange: (column: string) => void;
}

export function VendorsTable({
  vendors,
  isLoading,
  page,
  pageSize,
  totalPages,
  totalCount,
  sortBy,
  sortOrder,
  onPageChange,
  onPageSizeChange,
  onSortChange,
}: VendorsTableProps) {
  const router = useRouter();

  function getSortIcon(columnId: string) {
    if (sortBy !== columnId) return <ArrowUpDown className="h-3 w-3 ml-1" />;
    return sortOrder === 'asc' ? (
      <ArrowUp className="h-3 w-3 ml-1" />
    ) : (
      <ArrowDown className="h-3 w-3 ml-1" />
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    );
  }

  if (vendors.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center border rounded-md">
        <h3 className="text-lg font-medium">No vendors found</h3>
        <p className="text-sm text-muted-foreground">Try adjusting your filters.</p>
      </div>
    );
  }

  const sortableColumns = ['companyName', 'totalPurchases', 'status'];

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            {vendorTableColumns.map((col) => {
              const colId = col.id || (col as { accessorKey?: string }).accessorKey || '';
              const isSortable = sortableColumns.includes(colId);
              return (
                <TableHead
                  key={colId}
                  style={{ width: col.size }}
                  className={isSortable ? 'cursor-pointer select-none' : ''}
                  onClick={isSortable ? () => onSortChange(colId) : undefined}
                >
                  <div className="flex items-center">
                    {typeof col.header === 'string' ? col.header : ''}
                    {isSortable && getSortIcon(colId)}
                  </div>
                </TableHead>
              );
            })}
          </TableRow>
        </TableHeader>
        <TableBody>
          {vendors.map((vendor) => (
            <TableRow
              key={vendor.id}
              className="cursor-pointer"
              onClick={() => router.push(`/vendors/${vendor.id}`)}
            >
              {vendorTableColumns.map((col) => {
                const colId = col.id || (col as { accessorKey?: string }).accessorKey || '';
                return (
                  <TableCell
                    key={colId}
                    onClick={colId === 'actions' ? (e) => e.stopPropagation() : undefined}
                  >
                    {col.cell
                      ? (col.cell as (info: { row: { original: Vendor } }) => React.ReactNode)({
                          row: { original: vendor },
                        })
                      : ((vendor as unknown as Record<string, unknown>)[colId]?.toString() ?? '')}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, totalCount)} of{' '}
          {totalCount}
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Rows:</span>
            <Select value={pageSize.toString()} onValueChange={(v) => onPageSizeChange(Number(v))}>
              <SelectTrigger className="w-[70px] h-8">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="10">10</SelectItem>
                <SelectItem value="20">20</SelectItem>
                <SelectItem value="50">50</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </Button>
            <span className="text-sm">
              {page} / {totalPages || 1}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
