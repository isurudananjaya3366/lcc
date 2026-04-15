'use client';

import { useState } from 'react';
import {
  type SortingState,
  type ColumnDef,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  useReactTable,
  flexRender,
} from '@tanstack/react-table';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import type { APIKey } from '@/types/settings';

interface APIKeysTableProps {
  keys: APIKey[];
  onRevoke?: (apiKey: APIKey) => void;
}

function maskKey(key: string): string {
  if (key.length <= 12) return key;
  return `${key.slice(0, 8)}...${key.slice(-4)}`;
}

export function APIKeysTable({ keys, onRevoke }: APIKeysTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns: ColumnDef<APIKey>[] = [
    {
      accessorKey: 'name',
      header: 'Name',
      cell: ({ row }) => <span className="font-medium">{row.original.name}</span>,
    },
    {
      accessorKey: 'key',
      header: 'Key',
      enableSorting: false,
      cell: ({ row }) => (
        <code className="rounded bg-muted px-2 py-0.5 text-xs">{maskKey(row.original.key)}</code>
      ),
    },
    {
      accessorKey: 'createdAt',
      header: 'Created',
      cell: ({ row }) => formatDistanceToNow(new Date(row.original.createdAt), { addSuffix: true }),
    },
    {
      accessorKey: 'lastUsedAt',
      header: 'Last Used',
      cell: ({ row }) => {
        const lastUsed = row.original.lastUsedAt;
        if (!lastUsed) return <span className="text-muted-foreground">Never</span>;
        return formatDistanceToNow(new Date(lastUsed), { addSuffix: true });
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => {
        const status = row.original.status;
        return <Badge variant={status === 'ACTIVE' ? 'default' : 'destructive'}>{status}</Badge>;
      },
    },
    {
      id: 'actions',
      header: '',
      enableSorting: false,
      cell: ({ row }) =>
        row.original.status === 'ACTIVE' ? (
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive"
            onClick={() => onRevoke?.(row.original)}
          >
            Revoke
          </Button>
        ) : null,
    },
  ];

  const table = useReactTable({
    data: keys,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead
                    key={header.id}
                    className={header.column.getCanSort() ? 'cursor-pointer select-none' : ''}
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                    {header.column.getIsSorted() === 'asc' && ' ↑'}
                    {header.column.getIsSorted() === 'desc' && ' ↓'}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No API keys found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {table.getFilteredRowModel().rows.length} key(s)
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
