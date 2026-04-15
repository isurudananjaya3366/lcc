'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import type { TenantUser } from '@/types/settings';

interface DisableUserActionProps {
  user: TenantUser;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function DisableUserAction({ user, open, onClose, onSuccess }: DisableUserActionProps) {
  const [loading, setLoading] = useState(false);
  const isActive = user.status === 'ACTIVE';

  const handleConfirm = async () => {
    setLoading(true);
    // TODO: connect to API — PATCH /api/users/{userId}/status
    console.log('Toggle user status:', {
      userId: user.id,
      status: isActive ? 'DISABLED' : 'ACTIVE',
    });
    setLoading(false);
    onSuccess?.();
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isActive ? 'Disable User' : 'Enable User'}</DialogTitle>
          <DialogDescription>
            {isActive
              ? 'Are you sure you want to disable this user? They will not be able to access the system.'
              : 'Are you sure you want to enable this user? They will regain access.'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-2">
          <p className="text-sm">
            <span className="text-muted-foreground">User:</span>{' '}
            <span className="font-medium">{user.name}</span> ({user.email})
          </p>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant={isActive ? 'destructive' : 'default'}
            onClick={handleConfirm}
            disabled={loading}
          >
            {loading ? 'Processing...' : isActive ? 'Disable User' : 'Enable User'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
