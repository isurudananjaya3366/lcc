'use client';

import { Checkbox } from '@/components/ui/checkbox';
import type { Permission } from '@/types/settings';

interface PermissionCheckboxProps {
  permission: Permission;
  checked: boolean;
  onChange: (permissionId: string, checked: boolean) => void;
}

export function PermissionCheckbox({ permission, checked, onChange }: PermissionCheckboxProps) {
  return (
    <label className="flex items-center gap-2 rounded px-2 py-1 hover:bg-muted/50">
      <Checkbox
        checked={checked}
        onCheckedChange={(val) => onChange(permission.id, val === true)}
      />
      <span className="text-sm">{permission.name}</span>
    </label>
  );
}
