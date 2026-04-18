import type { Metadata } from 'next';
import { DashboardPage } from '@/components/storefront/portal/Dashboard';

export const metadata: Metadata = {
  title: 'Dashboard',
};

export default function DashboardRoute() {
  return <DashboardPage />;
}
