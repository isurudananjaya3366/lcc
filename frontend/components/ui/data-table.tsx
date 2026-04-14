'use client';

import * as React from 'react';
import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  type RowSelectionState,
  type PaginationState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { cn } from '@/lib/utils';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { TablePagination } from '@/components/ui/table-pagination';

export interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  sorting?: SortingState;
  onSortingChange?: (sorting: SortingState) => void;
  columnFilters?: ColumnFiltersState;
  onColumnFiltersChange?: (filters: ColumnFiltersState) => void;
  columnVisibility?: VisibilityState;
  onColumnVisibilityChange?: (visibility: VisibilityState) => void;
  rowSelection?: RowSelectionState;
  onRowSelectionChange?: (selection: RowSelectionState) => void;
  pagination?: PaginationState;
  onPaginationChange?: (pagination: PaginationState) => void;
  pageCount?: number;
  manualPagination?: boolean;
  manualSorting?: boolean;
  manualFiltering?: boolean;
  globalFilter?: string;
  onGlobalFilterChange?: (filter: string) => void;
  className?: string;
  emptyMessage?: string;
  showPagination?: boolean;
  pageSizeOptions?: number[];
}

function DataTable<TData, TValue>({
  columns,
  data,
  sorting: externalSorting,
  onSortingChange,
  columnFilters: externalFilters,
  onColumnFiltersChange,
  columnVisibility: externalVisibility,
  onColumnVisibilityChange,
  rowSelection: externalSelection,
  onRowSelectionChange,
  pagination: externalPagination,
  onPaginationChange,
  pageCount,
  manualPagination = false,
  manualSorting = false,
  manualFiltering = false,
  globalFilter: externalGlobalFilter,
  onGlobalFilterChange,
  className,
  emptyMessage = 'No results.',
  showPagination = false,
  pageSizeOptions,
}: DataTableProps<TData, TValue>) {
  const [internalSorting, setInternalSorting] = React.useState<SortingState>([]);
  const [internalFilters, setInternalFilters] = React.useState<ColumnFiltersState>([]);
  const [internalVisibility, setInternalVisibility] = React.useState<VisibilityState>({});
  const [internalSelection, setInternalSelection] = React.useState<RowSelectionState>({});
  const [internalGlobalFilter, setInternalGlobalFilter] = React.useState('');

  const sorting = externalSorting ?? internalSorting;
  const columnFilters = externalFilters ?? internalFilters;
  const columnVisibility = externalVisibility ?? internalVisibility;
  const rowSelection = externalSelection ?? internalSelection;
  const globalFilter = externalGlobalFilter ?? internalGlobalFilter;

  const table = useReactTable({
    data,
    columns,
    pageCount,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
      ...(externalPagination ? { pagination: externalPagination } : {}),
    },
    onSortingChange: (updater) => {
      const next = typeof updater === 'function' ? updater(sorting) : updater;
      onSortingChange ? onSortingChange(next) : setInternalSorting(next);
    },
    onColumnFiltersChange: (updater) => {
      const next = typeof updater === 'function' ? updater(columnFilters) : updater;
      onColumnFiltersChange ? onColumnFiltersChange(next) : setInternalFilters(next);
    },
    onColumnVisibilityChange: (updater) => {
      const next = typeof updater === 'function' ? updater(columnVisibility) : updater;
      onColumnVisibilityChange ? onColumnVisibilityChange(next) : setInternalVisibility(next);
    },
    onRowSelectionChange: (updater) => {
      const next = typeof updater === 'function' ? updater(rowSelection) : updater;
      onRowSelectionChange ? onRowSelectionChange(next) : setInternalSelection(next);
    },
    onGlobalFilterChange: (updater) => {
      const next = typeof updater === 'function' ? updater(globalFilter) : updater;
      onGlobalFilterChange ? onGlobalFilterChange(next) : setInternalGlobalFilter(next);
    },
    onPaginationChange: onPaginationChange
      ? (updater) => {
          const next =
            typeof updater === 'function'
              ? updater(externalPagination ?? { pageIndex: 0, pageSize: 10 })
              : updater;
          onPaginationChange(next);
        }
      : undefined,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: manualSorting ? undefined : getSortedRowModel(),
    getFilteredRowModel: manualFiltering ? undefined : getFilteredRowModel(),
    getPaginationRowModel: manualPagination ? undefined : getPaginationRowModel(),
    manualPagination,
    manualSorting,
    manualFiltering,
    enableRowSelection: true,
  });

  return (
    <div className={cn('rounded-md border', className)}>
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>
                  {header.isPlaceholder
                    ? null
                    : flexRender(header.column.columnDef.header, header.getContext())}
                </TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow key={row.id} data-state={row.getIsSelected() && 'selected'}>
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
                {emptyMessage}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      {showPagination && <TablePagination table={table} pageSizeOptions={pageSizeOptions} />}
    </div>
  );
}

export { DataTable };
