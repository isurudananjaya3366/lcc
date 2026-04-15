'use client';

import { PermissionGroup } from './PermissionGroup';
import type { Permission } from '@/types/settings';

// Default permission modules for the POS system
const DEFAULT_PERMISSIONS: Permission[] = [
  { id: 'dashboard_view', name: 'View Dashboard', group: 'Dashboard' },
  { id: 'products_view', name: 'View Products', group: 'Products' },
  { id: 'products_create', name: 'Create Products', group: 'Products' },
  { id: 'products_edit', name: 'Edit Products', group: 'Products' },
  { id: 'products_delete', name: 'Delete Products', group: 'Products' },
  { id: 'inventory_view', name: 'View Inventory', group: 'Inventory' },
  { id: 'inventory_adjust', name: 'Adjust Inventory', group: 'Inventory' },
  { id: 'inventory_transfer', name: 'Transfer Inventory', group: 'Inventory' },
  { id: 'sales_view', name: 'View Sales', group: 'Sales' },
  { id: 'sales_create', name: 'Create Sales', group: 'Sales' },
  { id: 'sales_void', name: 'Void Sales', group: 'Sales' },
  { id: 'customers_view', name: 'View Customers', group: 'Customers' },
  { id: 'customers_create', name: 'Create Customers', group: 'Customers' },
  { id: 'customers_edit', name: 'Edit Customers', group: 'Customers' },
  { id: 'customers_delete', name: 'Delete Customers', group: 'Customers' },
  { id: 'vendors_view', name: 'View Vendors', group: 'Vendors' },
  { id: 'vendors_create', name: 'Create Vendors', group: 'Vendors' },
  { id: 'vendors_edit', name: 'Edit Vendors', group: 'Vendors' },
  { id: 'vendors_delete', name: 'Delete Vendors', group: 'Vendors' },
  { id: 'reports_view', name: 'View Reports', group: 'Reports' },
  { id: 'reports_export', name: 'Export Reports', group: 'Reports' },
  { id: 'settings_view', name: 'View Settings', group: 'Settings' },
  { id: 'settings_edit', name: 'Edit Settings', group: 'Settings' },
  { id: 'users_view', name: 'View Users', group: 'Users' },
  { id: 'users_invite', name: 'Invite Users', group: 'Users' },
  { id: 'users_edit', name: 'Edit Users', group: 'Users' },
  { id: 'users_remove', name: 'Remove Users', group: 'Users' },
  { id: 'roles_view', name: 'View Roles', group: 'Roles' },
  { id: 'roles_create', name: 'Create Roles', group: 'Roles' },
  { id: 'roles_edit', name: 'Edit Roles', group: 'Roles' },
  { id: 'roles_delete', name: 'Delete Roles', group: 'Roles' },
];

interface PermissionMatrixProps {
  selectedIds: string[];
  onChange: (permissionIds: string[]) => void;
}

export function PermissionMatrix({ selectedIds, onChange }: PermissionMatrixProps) {
  // Group permissions by their group field
  const groups = DEFAULT_PERMISSIONS.reduce<Record<string, Permission[]>>((acc, perm) => {
    const group = acc[perm.group] ?? [];
    group.push(perm);
    acc[perm.group] = group;
    return acc;
  }, {});

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium">Permissions</h4>
      <div className="grid gap-4 sm:grid-cols-2">
        {Object.entries(groups).map(([groupName, permissions]) => (
          <PermissionGroup
            key={groupName}
            groupName={groupName}
            permissions={permissions}
            selectedIds={selectedIds}
            onChange={onChange}
          />
        ))}
      </div>
    </div>
  );
}
