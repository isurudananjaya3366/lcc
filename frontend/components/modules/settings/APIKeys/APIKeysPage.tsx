'use client';

import { useState } from 'react';
import { Key, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { APIKeysTable } from './APIKeysTable';
import { GenerateKeyModal } from './GenerateKeyModal';
import { RevokeKeyAction } from './RevokeKeyAction';
import type { APIKey } from '@/types/settings';

// Placeholder data — will be replaced with API calls
const MOCK_KEYS: APIKey[] = [];

export function APIKeysPage() {
  const [generateOpen, setGenerateOpen] = useState(false);
  const [revokeKey, setRevokeKey] = useState<APIKey | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">API Keys</h2>
          <p className="text-muted-foreground">Manage API keys for programmatic access</p>
        </div>
        <Button onClick={() => setGenerateOpen(true)}>
          <Key className="mr-2 h-4 w-4" />
          Generate New Key
        </Button>
      </div>

      <APIKeysTable keys={MOCK_KEYS} onRevoke={(key) => setRevokeKey(key)} />

      <div className="flex items-start gap-2 rounded-md border border-yellow-300 bg-yellow-50 p-3 text-sm dark:border-yellow-700 dark:bg-yellow-900/20">
        <AlertTriangle className="mt-0.5 h-4 w-4 text-yellow-600 dark:text-yellow-400" />
        <p className="text-yellow-800 dark:text-yellow-200">
          API keys are sensitive. Treat them like passwords. Never share or expose them in
          client-side code.
        </p>
      </div>

      <GenerateKeyModal open={generateOpen} onClose={() => setGenerateOpen(false)} />

      {revokeKey && (
        <RevokeKeyAction apiKey={revokeKey} open={!!revokeKey} onClose={() => setRevokeKey(null)} />
      )}
    </div>
  );
}
