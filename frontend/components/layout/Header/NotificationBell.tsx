'use client';

import { useCallback, useState } from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { cn } from '@/lib/cn';
import { NotificationItem, type NotificationData } from './NotificationItem';

// Placeholder notifications — will be replaced by a real store/API
const MOCK_NOTIFICATIONS: NotificationData[] = [
  {
    id: '1',
    type: 'order',
    title: 'New order received',
    message: 'Order #1042 placed by Kamal Perera — LKR 12,500.00',
    timestamp: new Date(Date.now() - 5 * 60_000).toISOString(),
    read: false,
  },
  {
    id: '2',
    type: 'inventory',
    title: 'Low stock alert',
    message: 'Basmati Rice 5kg is below reorder level (12 remaining)',
    timestamp: new Date(Date.now() - 30 * 60_000).toISOString(),
    read: false,
  },
  {
    id: '3',
    type: 'success',
    title: 'Payment confirmed',
    message: 'Invoice INV-2024-0098 payment of LKR 45,000 received',
    timestamp: new Date(Date.now() - 2 * 3600_000).toISOString(),
    read: true,
  },
];

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationData[]>(MOCK_NOTIFICATIONS);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const handleMarkRead = useCallback((id: string) => {
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  }, []);

  const handleMarkAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  return (
    <div className="relative">
      {/* Bell trigger */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          'relative flex h-10 w-10 items-center justify-center rounded-lg transition-colors',
          'hover:bg-gray-100 dark:hover:bg-gray-700',
          isOpen && 'bg-gray-100 dark:bg-gray-700',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
        )}
        aria-label={`Notifications${unreadCount > 0 ? ` (${unreadCount} unread)` : ''}`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <Bell className="h-5 w-5 text-gray-600 dark:text-gray-300" />
        {unreadCount > 0 && (
          <span className="absolute right-1 top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop to close */}
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} aria-hidden="true" />

          <div
            className="absolute right-0 top-12 z-50 w-80 rounded-xl border bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800 sm:w-96"
            role="dialog"
            aria-label="Notifications"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b px-4 py-3 dark:border-gray-700">
              <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                Notifications
              </h3>
              {unreadCount > 0 && (
                <button
                  type="button"
                  onClick={handleMarkAllRead}
                  className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
                >
                  <CheckCheck className="h-3.5 w-3.5" />
                  Mark all read
                </button>
              )}
            </div>

            {/* List */}
            <div className="max-h-80 overflow-y-auto p-1">
              {notifications.length === 0 ? (
                <p className="py-8 text-center text-sm text-gray-500">No notifications</p>
              ) : (
                notifications.map((n) => (
                  <NotificationItem key={n.id} notification={n} onMarkRead={handleMarkRead} />
                ))
              )}
            </div>

            {/* Footer */}
            <div className="border-t px-4 py-2 dark:border-gray-700">
              <a
                href="/notifications"
                className="block text-center text-xs font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400"
              >
                View all notifications
              </a>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
