import type { Metadata } from 'next';
import { DashboardHome } from '@/components/dashboard/DashboardHome';

export const metadata: Metadata = {
  title: 'Dashboard',
  description: 'Overview of your business performance and key metrics.',
};

export default function DashboardPage() {
  return <DashboardHome />;
}
