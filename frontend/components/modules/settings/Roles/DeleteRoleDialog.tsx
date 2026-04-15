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
import type { Role } from '@/types/settings';

interface DeleteRoleDialogProps {
  role: Role;
  open: boolean;
  onClose: () => void;
  onConfirm?: () => void;
}

export function DeleteRoleDialog({ role, open, onClose, onConfirm }: DeleteRoleDialogProps) {
  const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false);
  const isConfirmed = confirmation === role.name;

  if (role.isSystem) {
    return (
      <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Cannot Delete System Role</DialogTitle>
            <DialogDescription>
              System roles cannot be deleted. They are required for the application to function.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end">
            <Button onClick={onClose}>Close</Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  const handleDelete = async () => {
    if (!isConfirmed) return;
    setLoading(true);
    // TODO: connect to API — DELETE /api/roles/{roleId}
    console.log('Delete role:', role.id);
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
            Delete Role
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to delete the &quot;{role.name}&quot; role?
          </DialogDescription>
        </DialogHeader>

        {role.userCount > 0 && (
          <div className="rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm">
            <p className="font-medium text-destructive">
              ⚠️ {role.userCount} user{role.userCount !== 1 ? 's are' : ' is'} assigned to this
              role.
            </p>
            <p className="mt-1 text-muted-foreground">
              Please reassign these users before deleting.
            </p>
          </div>
        )}

        <div className="space-y-2">
          <Label>
            Type <strong>&quot;{role.name}&quot;</strong> to confirm:
          </Label>
          <Input
            value={confirmation}
            onChange={(e) => setConfirmation(e.target.value)}
            placeholder={role.name}
          />
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleDelete} disabled={!isConfirmed || loading}>
            {loading ? 'Deleting...' : 'Delete Role'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
