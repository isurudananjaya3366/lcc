'use client';

import { MoreVertical, Pencil, Lock, Unlock, Trash } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { TenantUser } from '@/types/settings';

interface UserActionsCellProps {
  user: TenantUser;
  onEdit?: (user: TenantUser) => void;
  onDisableToggle?: (user: TenantUser) => void;
  onRemove?: (user: TenantUser) => void;
}

export function UserActionsCell({ user, onEdit, onDisableToggle, onRemove }: UserActionsCellProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">Actions</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => onEdit?.(user)}>
          <Pencil className="mr-2 h-4 w-4" />
          Edit
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => onDisableToggle?.(user)}>
          {user.status === 'ACTIVE' ? (
            <>
              <Lock className="mr-2 h-4 w-4" />
              Disable
            </>
          ) : (
            <>
              <Unlock className="mr-2 h-4 w-4" />
              Enable
            </>
          )}
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="text-destructive" onClick={() => onRemove?.(user)}>
          <Trash className="mr-2 h-4 w-4" />
          Remove
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
