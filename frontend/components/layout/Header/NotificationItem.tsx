'use client';

import { formatDistanceToNow } from 'date-fns';
import type { LucideIcon } from 'lucide-react';
import { Package, ShoppingCart, AlertTriangle, Info, Check } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface NotificationData {
  id: string;
  type: 'info' | 'success' | 'warning' | 'order' | 'inventory';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  href?: string;
}

const typeIcons: Record<NotificationData['type'], LucideIcon> = {
  info: Info,
  success: Check,
  warning: AlertTriangle,
  order: ShoppingCart,
  inventory: Package,
};

const typeColors: Record<NotificationData['type'], string> = {
  info: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  success: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  warning: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
  order: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400',
  inventory: 'bg-cyan-100 text-cyan-600 dark:bg-cyan-900/30 dark:text-cyan-400',
};

interface NotificationItemProps {
  notification: NotificationData;
  onMarkRead: (id: string) => void;
  onClick?: (notification: NotificationData) => void;
}

export function NotificationItem({ notification, onMarkRead, onClick }: NotificationItemProps) {
  const Icon = typeIcons[notification.type];

  return (
    <button
      type="button"
      onClick={() => {
        if (!notification.read) onMarkRead(notification.id);
        onClick?.(notification);
      }}
      className={cn(
        'flex w-full items-start gap-3 rounded-md px-3 py-2.5 text-left transition-colors',
        'hover:bg-gray-100 dark:hover:bg-gray-700',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
        !notification.read && 'bg-blue-50/50 dark:bg-blue-900/10'
      )}
    >
      {/* Icon */}
      <div
        className={cn(
          'mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
          typeColors[notification.type]
        )}
      >
        <Icon className="h-4 w-4" />
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <p
            className={cn(
              'truncate text-sm',
              !notification.read
                ? 'font-medium text-gray-900 dark:text-gray-100'
                : 'text-gray-700 dark:text-gray-300'
            )}
          >
            {notification.title}
          </p>
          {!notification.read && (
            <span
              className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-blue-500"
              aria-label="Unread"
            />
          )}
        </div>
        <p className="mt-0.5 line-clamp-2 text-xs text-gray-500 dark:text-gray-400">
          {notification.message}
        </p>
        <p className="mt-1 text-[11px] text-gray-400">
          {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
        </p>
      </div>
    </button>
  );
}
