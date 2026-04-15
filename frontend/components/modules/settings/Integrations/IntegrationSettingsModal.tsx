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
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { Integration } from '@/types/settings';

interface IntegrationSettingsModalProps {
  integration: Integration;
  open: boolean;
  onClose: () => void;
  onDisconnect?: () => void;
}

export function IntegrationSettingsModal({
  integration,
  open,
  onClose,
  onDisconnect,
}: IntegrationSettingsModalProps) {
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showDisconnectConfirm, setShowDisconnectConfirm] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    // TODO: connect to API — PATCH /api/integrations/{id}/settings
    console.log('Save integration settings:', integration.id);
    setLoading(false);
    onClose();
  };

  const handleTest = async () => {
    setTesting(true);
    // TODO: connect to API — POST /api/integrations/{id}/test
    console.log('Test integration:', integration.id);
    setTesting(false);
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{integration.name} Settings</DialogTitle>
          <DialogDescription>Configure integration credentials and options</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>API Key</Label>
            <Input type="password" placeholder="Enter API key" />
          </div>

          <div className="space-y-2">
            <Label>Secret Key</Label>
            <Input type="password" placeholder="Enter secret key" />
          </div>

          {integration.configUrl && (
            <div className="space-y-2">
              <Label>Webhook URL</Label>
              <Input value={integration.configUrl} readOnly className="bg-muted" />
            </div>
          )}

          {integration.lastSync && (
            <p className="text-xs text-muted-foreground">
              Last synced: {new Date(integration.lastSync).toLocaleString()}
            </p>
          )}
        </div>

        <div className="flex justify-between">
          <Button variant="destructive" size="sm" onClick={() => setShowDisconnectConfirm(true)}>
            Disconnect
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleTest} disabled={testing}>
              {testing ? 'Testing...' : 'Test Connection'}
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              {loading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </div>

        {showDisconnectConfirm && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 space-y-3">
            <p className="text-sm font-medium text-destructive">
              Are you sure you want to disconnect {integration.name}?
            </p>
            <p className="text-xs text-muted-foreground">
              Data synchronization will stop immediately. You can reconnect later.
            </p>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" size="sm" onClick={() => setShowDisconnectConfirm(false)}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  setShowDisconnectConfirm(false);
                  onDisconnect?.();
                }}
              >
                Confirm Disconnect
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
