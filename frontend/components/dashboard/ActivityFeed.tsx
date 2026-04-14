'use client';

import { useMemo } from 'react';
import {
  ShoppingCart,
  Package,
  FileText,
  UserPlus,
  CreditCard,
  RefreshCw,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/cn';

// ─── Types ──────────────────────────────────────────────────────

export type ActivityType = 'sale' | 'product' | 'invoice' | 'customer' | 'payment' | 'refund';

export interface ActivityEvent {
  id: string;
  type: ActivityType;
  title: string;
  description: string;
  timestamp: string; // ISO 8601
}

// ─── Config ─────────────────────────────────────────────────────

const typeConfig: Record<ActivityType, { icon: LucideIcon; color: string; bg: string }> = {
  sale: {
    icon: ShoppingCart,
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-100 dark:bg-blue-900/30',
  },
  product: {
    icon: Package,
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-100 dark:bg-green-900/30',
  },
  invoice: {
    icon: FileText,
    color: 'text-purple-600 dark:text-purple-400',
    bg: 'bg-purple-100 dark:bg-purple-900/30',
  },
  customer: {
    icon: UserPlus,
    color: 'text-orange-600 dark:text-orange-400',
    bg: 'bg-orange-100 dark:bg-orange-900/30',
  },
  payment: {
    icon: CreditCard,
    color: 'text-emerald-600 dark:text-emerald-400',
    bg: 'bg-emerald-100 dark:bg-emerald-900/30',
  },
  refund: {
    icon: RefreshCw,
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-100 dark:bg-red-900/30',
  },
};

// ─── Helpers ────────────────────────────────────────────────────

function formatRelativeTime(isoDate: string): string {
  const now = Date.now();
  const then = new Date(isoDate).getTime();
  const diffMs = now - then;
  const diffMin = Math.floor(diffMs / 60_000);

  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay === 1) return 'Yesterday';
  if (diffDay < 7) return `${diffDay}d ago`;
  return new Date(isoDate).toLocaleDateString();
}

function getDateGroup(isoDate: string): string {
  const date = new Date(isoDate);
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) return 'Today';
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday';
  return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
}

// ─── Mock Data ──────────────────────────────────────────────────

const mockActivities: ActivityEvent[] = [
  {
    id: '1',
    type: 'sale',
    title: 'New sale completed',
    description: 'Order #1042 — LKR 8,500',
    timestamp: new Date(Date.now() - 2 * 60_000).toISOString(),
  },
  {
    id: '2',
    type: 'payment',
    title: 'Payment received',
    description: 'Invoice #INV-2024-089 — LKR 15,200',
    timestamp: new Date(Date.now() - 15 * 60_000).toISOString(),
  },
  {
    id: '3',
    type: 'product',
    title: 'Stock updated',
    description: 'Ceylon Tea 500g — 150 units added',
    timestamp: new Date(Date.now() - 45 * 60_000).toISOString(),
  },
  {
    id: '4',
    type: 'customer',
    title: 'New customer registered',
    description: 'Perera Enterprises — Colombo',
    timestamp: new Date(Date.now() - 2 * 3600_000).toISOString(),
  },
  {
    id: '5',
    type: 'invoice',
    title: 'Invoice generated',
    description: 'INV-2024-090 — LKR 42,000',
    timestamp: new Date(Date.now() - 4 * 3600_000).toISOString(),
  },
  {
    id: '6',
    type: 'refund',
    title: 'Refund processed',
    description: 'Order #1038 — LKR 2,300',
    timestamp: new Date(Date.now() - 6 * 3600_000).toISOString(),
  },
  {
    id: '7',
    type: 'sale',
    title: 'New sale completed',
    description: 'Order #1041 — LKR 3,750',
    timestamp: new Date(Date.now() - 25 * 3600_000).toISOString(),
  },
  {
    id: '8',
    type: 'payment',
    title: 'Payment received',
    description: 'Invoice #INV-2024-088 — LKR 9,100',
    timestamp: new Date(Date.now() - 26 * 3600_000).toISOString(),
  },
];

// ─── Activity Item ──────────────────────────────────────────────

function ActivityItem({ event }: { event: ActivityEvent }) {
  const config = typeConfig[event.type];
  const Icon = config.icon;

  return (
    <div className="flex items-start gap-3 py-3">
      <div
        className={cn(
          'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          config.bg
        )}
      >
        <Icon className={cn('h-4 w-4', config.color)} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{event.title}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">{event.description}</p>
      </div>
      <span className="shrink-0 text-xs text-gray-400 dark:text-gray-500">
        {formatRelativeTime(event.timestamp)}
      </span>
    </div>
  );
}

// ─── Activity Feed ──────────────────────────────────────────────

interface ActivityFeedProps {
  activities?: ActivityEvent[];
  isLoading?: boolean;
}

export function ActivityFeed({ activities, isLoading }: ActivityFeedProps) {
  const items = activities ?? mockActivities;

  // Group by date
  const grouped = useMemo(() => {
    const groups = new Map<string, ActivityEvent[]>();
    for (const event of items) {
      const key = getDateGroup(event.timestamp);
      const list = groups.get(key) ?? [];
      list.push(event);
      groups.set(key, list);
    }
    return groups;
  }, [items]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="h-8 w-8 animate-pulse rounded-full bg-gray-200 dark:bg-gray-700" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
              <div className="h-3 w-1/2 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="max-h-[400px] overflow-y-auto">
      {Array.from(grouped.entries()).map(([label, events]) => (
        <div key={label}>
          <p className="sticky top-0 bg-white/90 py-1 text-xs font-semibold uppercase tracking-wider text-gray-400 backdrop-blur dark:bg-gray-800/90 dark:text-gray-500">
            {label}
          </p>
          <div className="divide-y divide-gray-100 dark:divide-gray-700/50">
            {events.map((event) => (
              <ActivityItem key={event.id} event={event} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
