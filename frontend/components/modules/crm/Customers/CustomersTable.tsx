'use client';

import { useRouter } from 'next/navigation';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { customerTableColumns } from './CustomerTableColumns';
import type { Customer } from '@/types/customer';

interface CustomersTableProps {
  data: Customer[];
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  page: number;
  pageSize: number;
  totalCount: number;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  onSortChange: (column: string) => void;
}

export function CustomersTable({
  data,
  isLoading,
  isError,
  error,
  page,
  pageSize,
  totalCount,
  sortBy,
  sortOrder,
  onPageChange,
  onPageSizeChange,
  onSortChange,
}: CustomersTableProps) {
  const router = useRouter();
  const totalPages = Math.ceil(totalCount / pageSize);
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalCount);

  const getSortIcon = (columnKey: string) => {
    if (sortBy !== columnKey) return <ArrowUpDown className="ml-1 h-3 w-3" />;
    return sortOrder === 'asc' ? (
      <ArrowUp className="ml-1 h-3 w-3" />
    ) : (
      <ArrowDown className="ml-1 h-3 w-3" />
    );
  };

  if (isError) {
    return (
      <div className="rounded-md border p-8 text-center text-sm text-muted-foreground">
        {error?.message || 'Failed to load customers.'}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              {customerTableColumns.map((col) => {
                const key = col.id ?? (col as { accessorKey?: string }).accessorKey ?? '';
                const sortable = col.enableSorting !== false && key !== 'actions';
                return (
                  <TableHead
                    key={key}
                    style={{ width: col.size }}
                    className={sortable ? 'cursor-pointer select-none' : ''}
                    onClick={sortable ? () => onSortChange(key) : undefined}
                  >
                    <span className="flex items-center">
                      {typeof col.header === 'string' ? col.header : ''}
                      {sortable && getSortIcon(key)}
                    </span>
                  </TableHead>
                );
              })}
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {customerTableColumns.map((col, j) => (
                    <TableCell key={j}>
                      <div className="h-5 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : data.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={customerTableColumns.length}
                  className="h-32 text-center text-muted-foreground"
                >
                  No customers found.
                </TableCell>
              </TableRow>
            ) : (
              data.map((customer) => (
                <TableRow
                  key={customer.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => router.push(`/customers/${customer.id}`)}
                >
                  {customerTableColumns.map((col) => {
                    const key = col.id ?? (col as { accessorKey?: string }).accessorKey ?? '';
                    const accessorKey = (col as { accessorKey?: string }).accessorKey;
                    const value = accessorKey
                      ? (customer as unknown as Record<string, unknown>)[accessorKey]
                      : undefined;

                    if (col.cell && typeof col.cell === 'function') {
                      return (
                        <TableCell
                          key={key}
                          onClick={key === 'actions' ? (e) => e.stopPropagation() : undefined}
                        >
                          {(col.cell as Function)({
                            row: { original: customer },
                            getValue: () => value,
                          })}
                        </TableCell>
                      );
                    }

                    return <TableCell key={key}>{value != null ? String(value) : '—'}</TableCell>;
                  })}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalCount > 0 && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            Showing {start}–{end} of {totalCount.toLocaleString()}
          </span>
          <div className="flex items-center gap-2">
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
              className="rounded border px-2 py-1 text-sm"
            >
              {[10, 25, 50, 100].map((s) => (
                <option key={s} value={s}>
                  {s} per page
                </option>
              ))}
            </select>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
            >
              Previous
            </Button>
            <span className="px-2">
              Page {page} of {totalPages}
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
      )}
    </div>
  );
}
