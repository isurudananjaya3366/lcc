'use client';

import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface RolesHeaderProps {
  onAddClick: () => void;
}

export function RolesHeader({ onAddClick }: RolesHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Roles & Permissions</h2>
        <p className="text-muted-foreground">Manage user roles and permission settings</p>
      </div>
      <Button onClick={onAddClick}>
        <Plus className="mr-2 h-4 w-4" />
        Add Role
      </Button>
    </div>
  );
}
