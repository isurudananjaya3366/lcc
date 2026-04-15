'use client';

import { useState } from 'react';
import { IntegrationsGrid } from './IntegrationsGrid';
import { IntegrationSettingsModal } from './IntegrationSettingsModal';
import type { Integration } from '@/types/settings';

// Placeholder data — will be replaced with API calls
const MOCK_INTEGRATIONS: Integration[] = [
  {
    id: '1',
    name: 'Stripe',
    description: 'Payment processing',
    category: 'payment',
    status: 'DISCONNECTED',
  },
  {
    id: '2',
    name: 'PayPal',
    description: 'Online payments',
    category: 'payment',
    status: 'DISCONNECTED',
  },
  {
    id: '3',
    name: 'SMS Gateway',
    description: 'SMS notifications',
    category: 'communication',
    status: 'DISCONNECTED',
  },
  {
    id: '4',
    name: 'Email Service',
    description: 'Transactional email delivery',
    category: 'communication',
    status: 'DISCONNECTED',
  },
  {
    id: '5',
    name: 'Accounting Software',
    description: 'Financial data sync',
    category: 'business',
    status: 'DISCONNECTED',
  },
  {
    id: '6',
    name: 'Shipping Provider',
    description: 'Shipping label generation',
    category: 'business',
    status: 'DISCONNECTED',
  },
];

export function IntegrationsPage() {
  const [settingsIntegration, setSettingsIntegration] = useState<Integration | null>(null);

  const handleConnect = (integration: Integration) => {
    // TODO: implement OAuth flow or open settings
    console.log('Connect:', integration.id);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Integrations</h2>
        <p className="text-muted-foreground">
          Connect third-party services to extend functionality
        </p>
      </div>

      <IntegrationsGrid
        integrations={MOCK_INTEGRATIONS}
        onConnect={handleConnect}
        onSettings={(integration) => setSettingsIntegration(integration)}
      />

      {settingsIntegration && (
        <IntegrationSettingsModal
          integration={settingsIntegration}
          open={!!settingsIntegration}
          onClose={() => setSettingsIntegration(null)}
        />
      )}
    </div>
  );
}
