'use client';

import { useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { TenantUser } from '@/types/settings';

interface RemoveUserDialogProps {
  user: TenantUser;
  open: boolean;
  onClose: () => void;
  onConfirm?: () => void;
}

export function RemoveUserDialog({ user, open, onClose, onConfirm }: RemoveUserDialogProps) {
  const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false);
  const isConfirmed = confirmation === 'DELETE' || confirmation === user.email;

  const handleRemove = async () => {
    if (!isConfirmed) return;
    setLoading(true);
    // TODO: connect to API — DELETE /api/users/{userId}
    console.log('Remove user:', user.id);
    setLoading(false);
    setConfirmation('');
    onConfirm?.();
    onClose();
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(isOpen) => {
        if (!isOpen) {
          setConfirmation('');
          onClose();
        }
      }}
    >
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Remove User
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to remove <strong>{user.email}</strong>?
          </DialogDescription>
        </DialogHeader>

        <div className="rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm">
          <p className="mb-2 font-medium text-destructive">
            ⚠️ WARNING: This action cannot be undone
          </p>
          <ul className="list-inside list-disc space-y-1 text-muted-foreground">
            <li>User will lose all access</li>
            <li>User data will be archived</li>
            <li>Historical records will be preserved</li>
          </ul>
        </div>

        <div className="space-y-2">
          <Label>
            Type <strong>&quot;DELETE&quot;</strong> to confirm:
          </Label>
          <Input
            value={confirmation}
            onChange={(e) => setConfirmation(e.target.value)}
            placeholder="DELETE"
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleRemove} disabled={!isConfirmed || loading}>
            {loading ? 'Removing...' : 'Remove User'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
