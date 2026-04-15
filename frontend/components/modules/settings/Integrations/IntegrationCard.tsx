'use client';

import { Settings, Link2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { IntegrationStatus } from './IntegrationStatus';
import type { Integration } from '@/types/settings';

interface IntegrationCardProps {
  integration: Integration;
  onConnect?: (integration: Integration) => void;
  onSettings?: (integration: Integration) => void;
  onDisconnect?: (integration: Integration) => void;
}

export function IntegrationCard({
  integration,
  onConnect,
  onSettings,
  onDisconnect,
}: IntegrationCardProps) {
  const isConnected = integration.status === 'CONNECTED';

  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            {integration.icon ? (
              <img src={integration.icon} alt={integration.name} className="h-10 w-10 rounded" />
            ) : (
              <div className="flex h-10 w-10 items-center justify-center rounded bg-primary/10">
                <Link2 className="h-5 w-5 text-primary" />
              </div>
            )}
            <div>
              <CardTitle className="text-base">{integration.name}</CardTitle>
              <p className="text-sm text-muted-foreground">{integration.description}</p>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <IntegrationStatus status={integration.status} />
          {isConnected ? (
            <Button variant="outline" size="sm" onClick={() => onSettings?.(integration)}>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          ) : (
            <Button size="sm" onClick={() => onConnect?.(integration)}>
              Connect
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
