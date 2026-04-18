'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Bell, Loader2 } from 'lucide-react';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import {
  getNotificationPrefs,
  updateNotificationPrefs,
  type NotificationPrefs,
} from '@/services/storefront/portalService';
import { PORTAL_TEST_IDS } from '../PortalTestIds';

export function NotificationSettings() {
  const [prefs, setPrefs] = useState<NotificationPrefs | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNotificationPrefs()
      .then(setPrefs)
      .finally(() => setLoading(false));
  }, []);

  const handleToggle = async (key: keyof NotificationPrefs, value: boolean) => {
    if (!prefs) return;
    const updated = { ...prefs, [key]: value };
    setPrefs(updated);
    try {
      await updateNotificationPrefs(updated);
      toast.success('Notification preferences updated');
    } catch {
      setPrefs(prefs);
      toast.error('Failed to update preferences');
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (!prefs) return null;

  const items: { key: keyof NotificationPrefs; label: string; description: string }[] = [
    {
      key: 'orderUpdates',
      label: 'Order Updates',
      description: 'Receive email notifications about your order status changes.',
    },
    {
      key: 'promotions',
      label: 'Promotions',
      description: 'Receive emails about sales, discounts, and special offers.',
    },
    {
      key: 'newsletter',
      label: 'Newsletter',
      description: 'Receive our weekly newsletter with new products and tips.',
    },
    {
      key: 'smsNotifications',
      label: 'SMS Notifications',
      description: 'Receive text messages for important order updates.',
    },
  ];

  return (
    <Card data-testid={PORTAL_TEST_IDS.notificationSettings}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Notification Preferences
        </CardTitle>
        <CardDescription>
          Choose how you want to be notified about updates and promotions.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {items.map((item, index) => (
          <div key={item.key}>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <p className="text-sm font-medium">{item.label}</p>
                <p className="text-xs text-muted-foreground">{item.description}</p>
              </div>
              <Switch
                checked={prefs[item.key]}
                onCheckedChange={(value) => handleToggle(item.key, value)}
              />
            </div>
            {index < items.length - 1 && <Separator className="mt-4" />}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
