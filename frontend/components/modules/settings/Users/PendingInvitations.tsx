'use client';

import { RefreshCw, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { UserInvitation } from '@/types/settings';
import { formatDistanceToNow } from 'date-fns';

interface PendingInvitationsProps {
  invitations: UserInvitation[];
  onResend?: (invitation: UserInvitation) => void;
  onCancel?: (invitation: UserInvitation) => void;
}

export function PendingInvitations({ invitations, onResend, onCancel }: PendingInvitationsProps) {
  if (invitations.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Pending Invitations</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {invitations.map((invitation) => (
            <div
              key={invitation.id}
              className="flex items-center justify-between rounded-lg border p-3"
            >
              <div className="space-y-1">
                <p className="text-sm font-medium">{invitation.email}</p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Role: {invitation.role}</span>
                  <span>·</span>
                  <span>
                    Sent {formatDistanceToNow(new Date(invitation.sentAt), { addSuffix: true })}
                  </span>
                  <span>·</span>
                  <Badge variant="outline" className="text-xs">
                    Expires{' '}
                    {formatDistanceToNow(new Date(invitation.expiresAt), { addSuffix: true })}
                  </Badge>
                </div>
              </div>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => onResend?.(invitation)}
                  title="Resend invitation"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-destructive"
                  onClick={() => onCancel?.(invitation)}
                  title="Cancel invitation"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
