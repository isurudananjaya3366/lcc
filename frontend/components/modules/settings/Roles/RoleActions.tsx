'use client';

import { Pencil, Trash } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { Role } from '@/types/settings';

interface RoleActionsProps {
  role: Role;
  onEdit: (role: Role) => void;
  onDelete: (role: Role) => void;
}

export function RoleActions({ role, onEdit, onDelete }: RoleActionsProps) {
  return (
    <div className="flex gap-1">
      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => onEdit(role)}>
        <Pencil className="h-4 w-4" />
        <span className="sr-only">Edit</span>
      </Button>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-destructive"
        onClick={() => onDelete(role)}
        disabled={role.isSystem}
        title={role.isSystem ? 'System roles cannot be deleted' : 'Delete role'}
      >
        <Trash className="h-4 w-4" />
        <span className="sr-only">Delete</span>
      </Button>
    </div>
  );
}
