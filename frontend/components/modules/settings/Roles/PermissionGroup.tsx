'use client';

import { Checkbox } from '@/components/ui/checkbox';
import { PermissionCheckbox } from './PermissionCheckbox';
import type { Permission } from '@/types/settings';

interface PermissionGroupProps {
  groupName: string;
  permissions: Permission[];
  selectedIds: string[];
  onChange: (permissionIds: string[]) => void;
}

export function PermissionGroup({
  groupName,
  permissions,
  selectedIds,
  onChange,
}: PermissionGroupProps) {
  const groupPermIds = permissions.map((p) => p.id);
  const selectedInGroup = groupPermIds.filter((id) => selectedIds.includes(id));
  const allSelected = selectedInGroup.length === permissions.length;
  const someSelected = selectedInGroup.length > 0 && !allSelected;

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const newIds = [...new Set([...selectedIds, ...groupPermIds])];
      onChange(newIds);
    } else {
      onChange(selectedIds.filter((id) => !groupPermIds.includes(id)));
    }
  };

  const handlePermissionChange = (permissionId: string, checked: boolean) => {
    if (checked) {
      onChange([...selectedIds, permissionId]);
    } else {
      onChange(selectedIds.filter((id) => id !== permissionId));
    }
  };

  return (
    <div className="space-y-2">
      <label className="flex items-center gap-2 font-medium">
        <Checkbox
          checked={allSelected}
          // @ts-expect-error -- indeterminate is valid for the underlying element
          indeterminate={someSelected}
          onCheckedChange={(val) => handleSelectAll(val === true)}
        />
        <span className="text-sm">{groupName}</span>
      </label>
      <div className="ml-6 space-y-1">
        {permissions.map((perm) => (
          <PermissionCheckbox
            key={perm.id}
            permission={perm}
            checked={selectedIds.includes(perm.id)}
            onChange={handlePermissionChange}
          />
        ))}
      </div>
    </div>
  );
}
