'use client';

import { RoleCard } from './RoleCard';
import type { Role } from '@/types/settings';

interface RolesListProps {
  roles: Role[];
  onEdit: (role: Role) => void;
  onDelete: (role: Role) => void;
}

export function RolesList({ roles, onEdit, onDelete }: RolesListProps) {
  if (roles.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md border border-dashed">
        <p className="text-muted-foreground">No roles found. Create your first role.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {roles.map((role) => (
        <RoleCard key={role.id} role={role} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );
}
