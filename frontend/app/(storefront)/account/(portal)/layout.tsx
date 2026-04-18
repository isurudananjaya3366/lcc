import type { Metadata } from 'next';
import { PortalLayout } from '@/components/storefront/portal';

export const metadata: Metadata = {
  title: {
    template: '%s | My Account',
    default: 'My Account',
  },
};

export default function PortalRouteLayout({ children }: { children: React.ReactNode }) {
  return <PortalLayout>{children}</PortalLayout>;
}
