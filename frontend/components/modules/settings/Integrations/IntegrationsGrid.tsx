'use client';

import { IntegrationCard } from './IntegrationCard';
import type { Integration } from '@/types/settings';

interface IntegrationsGridProps {
  integrations: Integration[];
  onConnect?: (integration: Integration) => void;
  onSettings?: (integration: Integration) => void;
  onDisconnect?: (integration: Integration) => void;
}

export function IntegrationsGrid({
  integrations,
  onConnect,
  onSettings,
  onDisconnect,
}: IntegrationsGridProps) {
  // Group by category
  const grouped = integrations.reduce<Record<string, Integration[]>>((acc, item) => {
    const group = acc[item.category] ?? [];
    group.push(item);
    acc[item.category] = group;
    return acc;
  }, {});

  const categoryLabels: Record<string, string> = {
    payment: 'Payment Processing',
    communication: 'Communication',
    business: 'Business Tools',
    other: 'Other',
  };

  if (integrations.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md border border-dashed">
        <p className="text-muted-foreground">No integrations available.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {Object.entries(grouped).map(([category, items]) => (
        <div key={category} className="space-y-4">
          <h3 className="text-lg font-semibold">{categoryLabels[category] ?? category}</h3>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((integration) => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                onConnect={onConnect}
                onSettings={onSettings}
                onDisconnect={onDisconnect}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
