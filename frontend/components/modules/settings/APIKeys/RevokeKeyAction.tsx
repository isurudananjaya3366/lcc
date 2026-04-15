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
import type { APIKey } from '@/types/settings';

interface RevokeKeyActionProps {
  apiKey: APIKey;
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function RevokeKeyAction({ apiKey, open, onClose, onSuccess }: RevokeKeyActionProps) {
  const [loading, setLoading] = useState(false);

  const handleRevoke = async () => {
    setLoading(true);
    // TODO: connect to API — DELETE /api/api-keys/{keyId}
    console.log('Revoke key:', apiKey.id);
    setLoading(false);
    onSuccess?.();
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Revoke API Key
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to revoke &quot;{apiKey.name}&quot;?
          </DialogDescription>
        </DialogHeader>

        <div className="rounded-md border border-destructive/20 bg-destructive/5 p-3 text-sm">
          <ul className="list-inside list-disc space-y-1 text-muted-foreground">
            <li>Applications using this key will immediately lose access</li>
            <li>This action cannot be undone</li>
            <li>Consider rotating to a new key first</li>
          </ul>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={handleRevoke} disabled={loading}>
            {loading ? 'Revoking...' : 'Revoke Key'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
