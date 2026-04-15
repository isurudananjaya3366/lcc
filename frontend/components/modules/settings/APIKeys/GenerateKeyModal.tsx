'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { APIKeyDisplay } from './APIKeyDisplay';

interface GenerateKeyModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function GenerateKeyModal({ open, onClose, onSuccess }: GenerateKeyModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!name.trim()) return;
    setLoading(true);
    // TODO: connect to API — POST /api/api-keys/generate
    // Mock generated key for now
    const mockKey = `sk_live_${crypto.randomUUID().replace(/-/g, '')}`;
    setGeneratedKey(mockKey);
    setLoading(false);
  };

  const handleClose = () => {
    setName('');
    setDescription('');
    setGeneratedKey(null);
    onSuccess?.();
    onClose();
  };

  if (generatedKey) {
    return <APIKeyDisplay apiKey={generatedKey} keyName={name} onClose={handleClose} />;
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Generate New API Key</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>API Key Name *</Label>
            <Input
              placeholder='e.g., "Production Key"'
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label>Description (optional)</Label>
            <Textarea
              placeholder="Brief description for this key"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              maxLength={200}
            />
          </div>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleGenerate} disabled={loading || !name.trim()}>
            {loading ? 'Generating...' : 'Generate'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
