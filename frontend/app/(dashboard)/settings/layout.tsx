import { ReactNode } from 'react';
import { SettingsLayout } from '@/components/modules/settings';

export default function SettingsRouteLayout({ children }: { children: ReactNode }) {
  return <SettingsLayout>{children}</SettingsLayout>;
}
