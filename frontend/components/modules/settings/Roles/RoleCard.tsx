'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { RoleUserCount } from './RoleUserCount';
import { RoleActions } from './RoleActions';
import type { Role } from '@/types/settings';

interface RoleCardProps {
  role: Role;
  onEdit: (role: Role) => void;
  onDelete: (role: Role) => void;
}

export function RoleCard({ role, onEdit, onDelete }: RoleCardProps) {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{role.name}</CardTitle>
          {role.isSystem && (
            <Badge variant="secondary" className="text-xs">
              System
            </Badge>
          )}
        </div>
        {role.description && <p className="text-sm text-muted-foreground">{role.description}</p>}
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <RoleUserCount count={role.userCount} />
          <RoleActions role={role} onEdit={onEdit} onDelete={onDelete} />
        </div>
      </CardContent>
    </Card>
  );
}
