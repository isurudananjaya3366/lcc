'use client';

import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { SettingsSectionCard } from './SettingsSectionCard';

interface NotificationSettingsProps {
  emailNotifications: boolean;
  pushNotifications: boolean;
  orderAlerts: boolean;
  inventoryAlerts: boolean;
  marketingEmails: boolean;
  onChange: (key: string, value: boolean) => void;
}

const NOTIFICATION_OPTIONS = [
  {
    key: 'emailNotifications',
    label: 'Email Notifications',
    description: 'Receive important updates via email',
  },
  {
    key: 'pushNotifications',
    label: 'Push Notifications',
    description: 'Get real-time notifications in browser',
  },
  {
    key: 'orderAlerts',
    label: 'Order Alerts',
    description: 'Notifications for new and updated orders',
  },
  {
    key: 'inventoryAlerts',
    label: 'Inventory Alerts',
    description: 'Low stock and reorder point notifications',
  },
  {
    key: 'marketingEmails',
    label: 'Marketing Emails',
    description: 'Product updates and promotional content',
  },
];

export function NotificationSettings({
  emailNotifications,
  pushNotifications,
  orderAlerts,
  inventoryAlerts,
  marketingEmails,
  onChange,
}: NotificationSettingsProps) {
  const values: Record<string, boolean> = {
    emailNotifications,
    pushNotifications,
    orderAlerts,
    inventoryAlerts,
    marketingEmails,
  };

  return (
    <SettingsSectionCard
      title="Notifications"
      description="Choose which notifications you want to receive."
    >
      <div className="space-y-4">
        {NOTIFICATION_OPTIONS.map((option) => (
          <div key={option.key} className="flex items-center justify-between rounded-lg border p-4">
            <div className="space-y-0.5">
              <Label htmlFor={option.key} className="text-sm font-medium">
                {option.label}
              </Label>
              <p className="text-xs text-muted-foreground">{option.description}</p>
            </div>
            <Switch
              id={option.key}
              checked={values[option.key] ?? false}
              onCheckedChange={(checked) => onChange(option.key, checked)}
            />
          </div>
        ))}
      </div>
    </SettingsSectionCard>
  );
}
