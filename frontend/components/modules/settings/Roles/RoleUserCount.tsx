'use client';

import { Users } from 'lucide-react';

interface RoleUserCountProps {
  count: number;
}

export function RoleUserCount({ count }: RoleUserCountProps) {
  const label = count === 0 ? 'No users' : count === 1 ? '1 user' : `${count} users`;

  return (
    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
      <Users className="h-3.5 w-3.5" />
      <span>{label}</span>
    </div>
  );
}
