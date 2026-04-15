'use client';

import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { SettingsSectionCard } from './SettingsSectionCard';

interface NotificationSettingsProps {
  emailNotifications: boolean;
  pushNotifications: boolean;
  orderAlerts: boolean;
  lowStockAlerts: boolean;
  dailyReports: boolean;
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
    key: 'lowStockAlerts',
    label: 'Low Stock Alerts',
    description: 'Notifications when inventory drops below reorder points',
  },
  {
    key: 'dailyReports',
    label: 'Daily Reports',
    description: 'Daily summary of sales, orders, and inventory activity',
  },
];

export function NotificationSettings({
  emailNotifications,
  pushNotifications,
  orderAlerts,
  lowStockAlerts,
  dailyReports,
  onChange,
}: NotificationSettingsProps) {
  const values: Record<string, boolean> = {
    emailNotifications,
    pushNotifications,
    orderAlerts,
    lowStockAlerts,
    dailyReports,
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
