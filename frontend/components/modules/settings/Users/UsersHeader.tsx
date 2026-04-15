'use client';

import { UserPlus } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface UsersHeaderProps {
  onInviteClick: () => void;
}

export function UsersHeader({ onInviteClick }: UsersHeaderProps) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">User Management</h2>
        <p className="text-muted-foreground">Manage users and invitations</p>
      </div>
      <Button onClick={onInviteClick}>
        <UserPlus className="mr-2 h-4 w-4" />
        Invite User
      </Button>
    </div>
  );
}
