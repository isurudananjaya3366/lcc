'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { Badge } from '@/components/ui/badge';
import { CustomerActionsCell } from './CustomerActionsCell';
import type { Customer } from '@/types/customer';

export const customerTableColumns: ColumnDef<Customer>[] = [
  {
    accessorKey: 'displayName',
    header: 'Name',
    enableSorting: true,
    size: 200,
    cell: ({ row }) => {
      const name = row.original.displayName;
      const initials = name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .slice(0, 2)
        .toUpperCase();
      return (
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary">
            {initials}
          </div>
          <span className="font-medium">{name}</span>
        </div>
      );
    },
  },
  {
    accessorKey: 'phone',
    header: 'Phone',
    enableSorting: false,
    size: 140,
  },
  {
    accessorKey: 'email',
    header: 'Email',
    enableSorting: false,
    size: 200,
    cell: ({ getValue }) => {
      const email = getValue<string>();
      return email ? (
        <a
          href={`mailto:${email}`}
          className="text-primary hover:underline"
          onClick={(e) => e.stopPropagation()}
        >
          {email}
        </a>
      ) : (
        <span className="text-muted-foreground">—</span>
      );
    },
  },
  {
    accessorKey: 'totalOrders',
    header: 'Orders',
    enableSorting: true,
    size: 80,
    cell: ({ getValue }) => (
      <div className="text-center">{(getValue<number>() ?? 0).toLocaleString()}</div>
    ),
  },
  {
    accessorKey: 'totalSpent',
    header: 'Balance (LKR)',
    enableSorting: true,
    size: 120,
    cell: ({ getValue }) => {
      const val = getValue<number>() ?? 0;
      return (
        <div className={`text-right ${val < 0 ? 'text-red-600' : ''}`}>
          ₨{val.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </div>
      );
    },
  },
  {
    accessorKey: 'status',
    header: 'Status',
    enableSorting: true,
    size: 100,
    cell: ({ getValue }) => {
      const status = getValue<string>();
      const isActive = status === 'ACTIVE';
      return (
        <Badge variant={isActive ? 'default' : 'secondary'}>
          {isActive ? 'Active' : 'Inactive'}
        </Badge>
      );
    },
  },
  {
    id: 'actions',
    header: '',
    enableSorting: false,
    size: 60,
    cell: ({ row }) => <CustomerActionsCell customer={row.original} />,
  },
];
