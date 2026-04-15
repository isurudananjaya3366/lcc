'use client';

import { useState } from 'react';
import { UsersHeader } from './UsersHeader';
import { UsersTable } from './UsersTable';
import { InviteUserModal } from './InviteUserModal';
import { EditUserModal } from './EditUserModal';
import { DisableUserAction } from './DisableUserAction';
import { RemoveUserDialog } from './RemoveUserDialog';
import { PendingInvitations } from './PendingInvitations';
import type { TenantUser, UserInvitation } from '@/types/settings';

// Placeholder data — will be replaced with API calls
const MOCK_USERS: TenantUser[] = [
  {
    id: '1',
    name: 'Admin User',
    email: 'admin@example.com',
    role: 'admin',
    status: 'ACTIVE',
    lastLogin: new Date().toISOString(),
    createdAt: '2024-01-01T00:00:00Z',
  },
];

const MOCK_INVITATIONS: UserInvitation[] = [];

export function UsersPage() {
  const [inviteOpen, setInviteOpen] = useState(false);
  const [editUser, setEditUser] = useState<TenantUser | null>(null);
  const [disableUser, setDisableUser] = useState<TenantUser | null>(null);
  const [removeUser, setRemoveUser] = useState<TenantUser | null>(null);

  return (
    <div className="space-y-6">
      <UsersHeader onInviteClick={() => setInviteOpen(true)} />

      <UsersTable
        data={MOCK_USERS}
        onEdit={(user) => setEditUser(user)}
        onDisableToggle={(user) => setDisableUser(user)}
        onRemove={(user) => setRemoveUser(user)}
      />

      <PendingInvitations invitations={MOCK_INVITATIONS} />

      <InviteUserModal open={inviteOpen} onClose={() => setInviteOpen(false)} />

      {editUser && (
        <EditUserModal user={editUser} open={!!editUser} onClose={() => setEditUser(null)} />
      )}

      {disableUser && (
        <DisableUserAction
          user={disableUser}
          open={!!disableUser}
          onClose={() => setDisableUser(null)}
        />
      )}

      {removeUser && (
        <RemoveUserDialog
          user={removeUser}
          open={!!removeUser}
          onClose={() => setRemoveUser(null)}
        />
      )}
    </div>
  );
}
