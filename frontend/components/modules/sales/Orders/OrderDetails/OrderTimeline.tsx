'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  FileText,
  CheckCircle,
  Clock,
  Truck,
  Package,
  XCircle,
  MessageSquare,
  CreditCard,
  Edit,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface TimelineEvent {
  id: string;
  eventType: 'status_change' | 'note_added' | 'payment' | 'update';
  statusFrom?: string;
  statusTo?: string;
  note?: string;
  userName: string;
  createdAt: string;
  metadata?: Record<string, unknown>;
}

interface OrderTimelineProps {
  timeline: TimelineEvent[];
  isLoading?: boolean;
  maxHeight?: string;
}

const eventIcons: Record<string, React.ElementType> = {
  DRAFT: FileText,
  PENDING: Clock,
  CONFIRMED: CheckCircle,
  PROCESSING: Clock,
  SHIPPED: Truck,
  DELIVERED: Package,
  COMPLETED: CheckCircle,
  CANCELLED: XCircle,
  REFUNDED: XCircle,
  note_added: MessageSquare,
  payment: CreditCard,
  update: Edit,
};

const dotColors: Record<string, string> = {
  DRAFT: 'bg-gray-400',
  PENDING: 'bg-yellow-500',
  CONFIRMED: 'bg-blue-500',
  PROCESSING: 'bg-indigo-500',
  SHIPPED: 'bg-purple-500',
  DELIVERED: 'bg-green-500',
  COMPLETED: 'bg-emerald-500',
  CANCELLED: 'bg-red-500',
  REFUNDED: 'bg-orange-500',
  note_added: 'bg-gray-500',
  payment: 'bg-green-500',
  update: 'bg-blue-500',
};

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString('en-LK', { month: 'short', day: 'numeric', year: 'numeric' });
}

function getEventTitle(event: TimelineEvent): string {
  if (event.eventType === 'status_change' && event.statusTo) {
    return `Order ${event.statusTo.replace(/_/g, ' ').toLowerCase()}`;
  }
  if (event.eventType === 'note_added') return 'Note added';
  if (event.eventType === 'payment') return 'Payment received';
  return 'Order updated';
}

function TimelineItem({ event, isLast }: { event: TimelineEvent; isLast: boolean }) {
  const iconKey =
    event.eventType === 'status_change' ? event.statusTo || 'update' : event.eventType;
  const Icon = eventIcons[iconKey] || Edit;
  const dotColor = dotColors[iconKey] || 'bg-gray-400';

  return (
    <div className="relative flex gap-4 pb-6">
      {/* Vertical line */}
      {!isLast && (
        <div className="absolute left-[15px] top-8 h-full w-0.5 bg-gray-200 dark:bg-gray-700" />
      )}
      {/* Dot / Icon */}
      <div
        className={cn(
          'relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white',
          dotColor
        )}
      >
        <Icon className="h-4 w-4" />
      </div>
      {/* Content */}
      <div className="flex-1 pt-1">
        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
          {getEventTitle(event)}
        </p>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span>{formatRelativeTime(event.createdAt)}</span>
          <span>·</span>
          <span>by {event.userName}</span>
        </div>
        {event.eventType === 'status_change' && event.statusFrom && event.statusTo && (
          <p className="mt-1 text-xs text-gray-500">
            {event.statusFrom.replace(/_/g, ' ')} → {event.statusTo.replace(/_/g, ' ')}
          </p>
        )}
        {event.note && (
          <p className="mt-1 rounded bg-gray-50 p-2 text-xs text-gray-600 dark:bg-gray-800 dark:text-gray-400">
            {event.note}
          </p>
        )}
      </div>
    </div>
  );
}

export function OrderTimeline({ timeline, isLoading, maxHeight = '600px' }: OrderTimelineProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Timeline</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <div className="h-8 w-8 animate-pulse rounded-full bg-gray-200 dark:bg-gray-700" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-32 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
                <div className="h-3 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const sorted = [...timeline].sort(
    (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        {sorted.length === 0 ? (
          <p className="py-4 text-center text-sm text-gray-500">No activity yet</p>
        ) : (
          <div className="overflow-y-auto" style={{ maxHeight }}>
            {sorted.map((event, idx) => (
              <TimelineItem key={event.id} event={event} isLast={idx === sorted.length - 1} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export type { TimelineEvent, OrderTimelineProps };
