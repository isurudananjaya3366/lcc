import type { Metadata } from 'next';
import { SettingsPage } from '@/components/storefront/portal/Settings';

export const metadata: Metadata = {
  title: 'Account Settings',
};

export default function SettingsRoute() {
  return <SettingsPage />;
}
