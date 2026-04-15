'use client';

import { ShoppingBag, Package, Calendar, UserPlus } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface CustomerQuickStatsProps {
  customer: {
    totalSpent: number;
    orderCount: number;
    lastOrderDate?: string;
    memberSince: string;
  };
  loading?: boolean;
  onOrdersClick?: () => void;
}

function formatCurrency(amount: number): string {
  if (amount >= 1_000_000) return `₨${(amount / 1_000_000).toFixed(1)}M`;
  if (amount >= 1_000) return `₨${(amount / 1_000).toFixed(1)}K`;
  return `₨${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function getRelativeDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
  return `${Math.floor(diffDays / 365)} years ago`;
}

function getDuration(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays < 30) return `${diffDays} days`;
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} months`;
  const years = Math.floor(diffDays / 365);
  const months = Math.floor((diffDays % 365) / 30);
  return months > 0 ? `${years}y ${months}m` : `${years} years`;
}

export function CustomerQuickStats({ customer, loading, onOrdersClick }: CustomerQuickStatsProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-20 mb-2" />
              <Skeleton className="h-6 w-24" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const stats = [
    {
      label: 'Total Spent',
      value: formatCurrency(customer.totalSpent),
      icon: ShoppingBag,
      iconColor: 'text-blue-500',
    },
    {
      label: 'Orders',
      value: customer.orderCount.toLocaleString(),
      icon: Package,
      iconColor: 'text-green-500',
      onClick: onOrdersClick,
    },
    {
      label: 'Last Order',
      value: customer.lastOrderDate ? getRelativeDate(customer.lastOrderDate) : 'Never',
      icon: Calendar,
      iconColor: 'text-orange-500',
    },
    {
      label: 'Member Since',
      value: customer.memberSince
        ? `${new Date(customer.memberSince).toLocaleDateString('en-LK', { month: 'short', year: 'numeric' })} (${getDuration(customer.memberSince)})`
        : 'N/A',
      icon: UserPlus,
      iconColor: 'text-purple-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <Card
          key={stat.label}
          className={stat.onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}
          onClick={stat.onClick}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <stat.icon className={`h-4 w-4 ${stat.iconColor}`} />
              {stat.label}
            </div>
            <p className="text-lg font-semibold">{stat.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
