'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { LocalizationSettings } from './LocalizationSettings';
import { NotificationSettings } from './NotificationSettings';
import type { GeneralSettings as GeneralSettingsType } from '@/types/settings';

const DEFAULT_SETTINGS: GeneralSettingsType = {
  timezone: 'Asia/Colombo',
  currency: 'LKR',
  dateFormat: 'DD/MM/YYYY',
  emailNotifications: true,
  pushNotifications: true,
  orderAlerts: true,
  inventoryAlerts: true,
  marketingEmails: false,
};

interface GeneralSettingsProps {
  initialSettings?: GeneralSettingsType;
}

export function GeneralSettings({ initialSettings }: GeneralSettingsProps) {
  const [settings, setSettings] = useState<GeneralSettingsType>(
    initialSettings ?? DEFAULT_SETTINGS
  );
  const [isSaving, setIsSaving] = useState(false);

  const handleNotificationChange = (key: string, value: boolean) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // API call would go here
      await new Promise((resolve) => setTimeout(resolve, 500));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">General Settings</h1>
        <p className="text-muted-foreground">
          Manage your account preferences and application settings.
        </p>
      </div>

      <LocalizationSettings
        timezone={settings.timezone}
        currency={settings.currency}
        dateFormat={settings.dateFormat}
        onTimezoneChange={(v) => setSettings((p) => ({ ...p, timezone: v }))}
        onCurrencyChange={(v) => setSettings((p) => ({ ...p, currency: v }))}
        onDateFormatChange={(v) => setSettings((p) => ({ ...p, dateFormat: v }))}
      />

      <NotificationSettings
        emailNotifications={settings.emailNotifications}
        pushNotifications={settings.pushNotifications}
        orderAlerts={settings.orderAlerts}
        inventoryAlerts={settings.inventoryAlerts}
        marketingEmails={settings.marketingEmails}
        onChange={handleNotificationChange}
      />

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save Changes'}
        </Button>
      </div>
    </div>
  );
}
