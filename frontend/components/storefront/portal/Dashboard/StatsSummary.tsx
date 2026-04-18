'use client';

import { Package, Clock, Heart, Star } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/cn';
import type { PortalStats } from '@/types/storefront/portal.types';

interface StatsSummaryProps {
  stats: PortalStats;
}

const statItems = [
  { key: 'totalOrders', label: 'Total Orders', icon: Package, color: 'text-blue-600' },
  { key: 'pendingOrders', label: 'Pending', icon: Clock, color: 'text-yellow-600' },
  { key: 'wishlistCount', label: 'Wishlist', icon: Heart, color: 'text-pink-600' },
  { key: 'reviewsCount', label: 'Reviews', icon: Star, color: 'text-amber-600' },
] as const;

export function StatsSummary({ stats }: StatsSummaryProps) {
  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {statItems.map(({ key, label, icon: Icon, color }) => (
        <Card key={key}>
          <CardContent className="pt-6 flex items-center gap-3">
            <div className={cn('rounded-lg bg-muted p-2.5', color)}>
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats[key]}</p>
              <p className="text-xs text-muted-foreground">{label}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
