'use client';

import { useState } from 'react';
import { RolesHeader } from './RolesHeader';
import { RolesList } from './RolesList';
import { AddRoleModal } from './AddRoleModal';
import { DeleteRoleDialog } from './DeleteRoleDialog';
import type { Role } from '@/types/settings';

// Placeholder data — will be replaced with API calls
const MOCK_ROLES: Role[] = [
  {
    id: '1',
    name: 'Admin',
    description: 'Full access to all features',
    permissions: [],
    userCount: 2,
    isSystem: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'Manager',
    description: 'Management and supervisory access',
    permissions: [],
    userCount: 3,
    isSystem: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '3',
    name: 'Cashier',
    description: 'Process sales only',
    permissions: [],
    userCount: 5,
    isSystem: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '4',
    name: 'Staff',
    description: 'Limited operational access',
    permissions: [],
    userCount: 4,
    isSystem: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
  {
    id: '5',
    name: 'Viewer',
    description: 'Read-only access',
    permissions: [],
    userCount: 1,
    isSystem: true,
    createdAt: '2024-01-01T00:00:00Z',
  },
];

export function RolesPage() {
  const [addOpen, setAddOpen] = useState(false);
  const [deleteRole, setDeleteRole] = useState<Role | null>(null);

  const handleEdit = (role: Role) => {
    // TODO: navigate to edit page or open modal
    console.log('Edit role:', role.id);
  };

  return (
    <div className="space-y-6">
      <RolesHeader onAddClick={() => setAddOpen(true)} />
      <RolesList roles={MOCK_ROLES} onEdit={handleEdit} onDelete={(role) => setDeleteRole(role)} />

      <AddRoleModal open={addOpen} onClose={() => setAddOpen(false)} />

      {deleteRole && (
        <DeleteRoleDialog
          role={deleteRole}
          open={!!deleteRole}
          onClose={() => setDeleteRole(null)}
        />
      )}
    </div>
  );
}
