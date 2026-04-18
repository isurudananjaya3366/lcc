'use client';

import { useState, useEffect } from 'react';
import { useStoreAuthStore } from '@/stores/store/auth';
import { getDashboardStats } from '@/services/storefront/portalService';
import type { PortalStats } from '@/types/storefront/portal.types';
import { WelcomeCard } from './WelcomeCard';
import { StatsSummary } from './StatsSummary';
import { RecentOrdersCard } from './RecentOrdersCard';
import { QuickActions } from './QuickActions';
import { DashboardLoading } from './DashboardLoading';

export function DashboardPage() {
  const user = useStoreAuthStore((s) => s.user);
  const [stats, setStats] = useState<PortalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats()
      .then(setStats)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !stats) {
    return <DashboardLoading />;
  }

  return (
    <div className="space-y-6">
      <WelcomeCard user={user} />
      <StatsSummary stats={stats} />
      <RecentOrdersCard />
      <QuickActions />
    </div>
  );
}
