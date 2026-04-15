'use client';

import { useState } from 'react';
import { Copy, Eye, EyeOff, AlertTriangle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface APIKeyDisplayProps {
  apiKey: string;
  keyName: string;
  onClose: () => void;
}

export function APIKeyDisplay({ apiKey, keyName, onClose }: APIKeyDisplayProps) {
  const [visible, setVisible] = useState(true);
  const [copied, setCopied] = useState(false);

  const displayKey = visible ? apiKey : apiKey.replace(/./g, '•');

  const handleCopy = async () => {
    await navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Dialog open onOpenChange={() => onClose()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Your New API Key</DialogTitle>
        </DialogHeader>

        <div className="rounded-md border border-yellow-300 bg-yellow-50 p-3 text-sm dark:border-yellow-700 dark:bg-yellow-900/20">
          <div className="flex items-center gap-2 font-medium text-yellow-800 dark:text-yellow-200">
            <AlertTriangle className="h-4 w-4" />
            Save this key now. You won&apos;t be able to see it again.
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Key name: <strong>{keyName}</strong>
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 rounded bg-muted p-3 font-mono text-sm break-all">
              {displayKey}
            </code>
            <div className="flex flex-col gap-1">
              <Button variant="outline" size="icon" className="h-8 w-8" onClick={handleCopy}>
                <Copy className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="h-8 w-8"
                onClick={() => setVisible(!visible)}
              >
                {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          {copied && (
            <p className="text-xs text-green-600 dark:text-green-400">Copied to clipboard!</p>
          )}
        </div>

        <ul className="list-inside list-disc space-y-1 text-xs text-muted-foreground">
          <li>This is your only chance to copy this key</li>
          <li>Store it in a secure location</li>
          <li>Never commit it to version control</li>
        </ul>

        <div className="flex justify-end">
          <Button onClick={onClose}>Done</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
