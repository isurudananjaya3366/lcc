'use client';

import { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  getExpandedRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table';
import {
  ChevronRight,
  Plus,
  Pencil,
  Trash2,
  LogIn,
  LogOut,
  Shield,
  Settings,
  Monitor,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { cn } from '@/lib/utils';
import type { AuditLogEntry } from '@/types/settings';

function getRelativeTime(timestamp: string) {
  const diff = Date.now() - new Date(timestamp).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(timestamp).toLocaleDateString('en-LK');
}

function getActionBadge(action: AuditLogEntry['action']) {
  const config: Record<
    AuditLogEntry['action'],
    { label: string; className: string; icon: React.ReactNode }
  > = {
    CREATE: {
      label: 'Create',
      className: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      icon: <Plus className="h-3 w-3" />,
    },
    UPDATE: {
      label: 'Update',
      className: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
      icon: <Pencil className="h-3 w-3" />,
    },
    DELETE: {
      label: 'Delete',
      className: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
      icon: <Trash2 className="h-3 w-3" />,
    },
    LOGIN: {
      label: 'Login',
      className: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
      icon: <LogIn className="h-3 w-3" />,
    },
    LOGOUT: {
      label: 'Logout',
      className: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
      icon: <LogOut className="h-3 w-3" />,
    },
    PERMISSION: {
      label: 'Permission',
      className: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
      icon: <Shield className="h-3 w-3" />,
    },
    SETTINGS: {
      label: 'Settings',
      className: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
      icon: <Settings className="h-3 w-3" />,
    },
    SYSTEM: {
      label: 'System',
      className: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
      icon: <Monitor className="h-3 w-3" />,
    },
  };

  const { label, className, icon } = config[action];
  return (
    <Badge className={cn('gap-1', className)}>
      {icon}
      {label}
    </Badge>
  );
}

interface AuditLogTableProps {
  entries: AuditLogEntry[];
  isLoading?: boolean;
}

export function AuditLogTable({ entries, isLoading }: AuditLogTableProps) {
  const [sorting, setSorting] = useState<SortingState>([
    { id: 'timestamp', desc: true },
  ]);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const columns = useMemo<ColumnDef<AuditLogEntry>[]>(
    () => [
      {
        id: 'expand',
        header: '',
        cell: ({ row }) => (
          <button
            onClick={() =>
              setExpanded((prev) => ({
                ...prev,
                [row.original.id]: !prev[row.original.id],
              }))
            }
            className="p-1"
          >
            <ChevronRight
              className={cn(
                'h-4 w-4 transition-transform',
                expanded[row.original.id] && 'rotate-90'
              )}
            />
          </button>
        ),
        size: 40,
      },
      {
        accessorKey: 'timestamp',
        header: 'Time',
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground" title={new Date(row.original.timestamp).toLocaleString('en-LK')}>
            {getRelativeTime(row.original.timestamp)}
          </span>
        ),
      },
      {
        accessorKey: 'userName',
        header: 'User',
        cell: ({ row }) => (
          <span className="text-sm font-medium">{row.original.userName}</span>
        ),
      },
      {
        accessorKey: 'action',
        header: 'Action',
        cell: ({ row }) => getActionBadge(row.original.action),
      },
      {
        accessorKey: 'entity',
        header: 'Entity',
        cell: ({ row }) => (
          <span className="text-sm">{row.original.entity}</span>
        ),
      },
      {
        accessorKey: 'details',
        header: 'Details',
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground line-clamp-1">
            {row.original.details}
          </span>
        ),
      },
      {
        accessorKey: 'ipAddress',
        header: 'IP Address',
        cell: ({ row }) => (
          <span className="text-xs font-mono text-muted-foreground">
            {row.original.ipAddress ?? '—'}
          </span>
        ),
      },
    ],
    [expanded]
  );

  const table = useReactTable({
    data: entries,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getExpandedRowModel: getExpandedRowModel(),
    initialState: { pagination: { pageSize: 50 } },
  });

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-12 animate-pulse rounded bg-gray-200 dark:bg-gray-700"
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <>
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </TableCell>
                    ))}
                  </TableRow>
                  {expanded[row.original.id] && (
                    <TableRow key={`${row.id}-expanded`}>
                      <TableCell colSpan={columns.length} className="bg-muted/50 p-4">
                        <div className="space-y-2 text-sm">
                          <p>
                            <span className="font-medium">Description: </span>
                            {row.original.details}
                          </p>
                          {row.original.entityId && (
                            <p>
                              <span className="font-medium">Entity ID: </span>
                              <span className="font-mono">
                                {row.original.entityId}
                              </span>
                            </p>
                          )}
                          {row.original.ipAddress && (
                            <p>
                              <span className="font-medium">IP Address: </span>
                              <span className="font-mono">
                                {row.original.ipAddress}
                              </span>
                            </p>
                          )}
                          <p>
                            <span className="font-medium">Full Timestamp: </span>
                            {new Date(row.original.timestamp).toLocaleString(
                              'en-LK'
                            )}
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No audit log entries found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {table.getState().pagination.pageIndex + 1} of{' '}
            {table.getPageCount()}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
