'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { UserStatusBadge } from './UserStatusBadge';
import { UserActionsCell } from './UserActionsCell';
import type { TenantUser } from '@/types/settings';
import { formatDistanceToNow } from 'date-fns';

interface UserColumnsOptions {
  onEdit?: (user: TenantUser) => void;
  onDisableToggle?: (user: TenantUser) => void;
  onRemove?: (user: TenantUser) => void;
}

export function getUserColumns(options: UserColumnsOptions = {}): ColumnDef<TenantUser>[] {
  return [
    {
      accessorKey: 'name',
      header: 'Name',
      cell: ({ row }) => {
        const user = row.original;
        return (
          <div className="flex items-center gap-3">
            {user.avatarUrl ? (
              <img
                src={user.avatarUrl}
                alt={user.name}
                className="h-8 w-8 rounded-full object-cover"
              />
            ) : (
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
                {user.name.charAt(0).toUpperCase()}
              </div>
            )}
            <span className="font-medium">{user.name}</span>
          </div>
        );
      },
    },
    {
      accessorKey: 'email',
      header: 'Email',
    },
    {
      accessorKey: 'role',
      header: 'Role',
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <UserStatusBadge status={row.original.status} />,
    },
    {
      accessorKey: 'lastLogin',
      header: 'Last Login',
      cell: ({ row }) => {
        const lastLogin = row.original.lastLogin;
        if (!lastLogin) return <span className="text-muted-foreground">Never</span>;
        return formatDistanceToNow(new Date(lastLogin), { addSuffix: true });
      },
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <UserActionsCell
          user={row.original}
          onEdit={options.onEdit}
          onDisableToggle={options.onDisableToggle}
          onRemove={options.onRemove}
        />
      ),
      enableSorting: false,
    },
  ];
}
