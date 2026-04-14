'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Package, Plus, ClipboardList, MoreHorizontal } from 'lucide-react';
import { cn } from '@/lib/cn';
import { isRouteActive } from '@/lib/navigation';

interface BottomNavItem {
  label: string;
  href: string;
  icon: React.ElementType;
  badge?: number;
  isAction?: boolean;
}

const bottomNavItems: BottomNavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Products', href: '/inventory/products', icon: Package },
  { label: 'New', href: '/sales/orders/new', icon: Plus, isAction: true },
  { label: 'Tasks', href: '/tasks', icon: ClipboardList },
  { label: 'More', href: '/settings', icon: MoreHorizontal },
];

/**
 * Fixed bottom navigation bar visible on mobile screens only.
 * Provides quick access to primary app sections.
 */
export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        'fixed inset-x-0 bottom-0 z-40 flex items-center justify-around border-t bg-white md:hidden',
        'dark:border-gray-700 dark:bg-gray-800',
        'pb-[env(safe-area-inset-bottom)]'
      )}
      style={{ height: 56 }}
      aria-label="Mobile navigation"
    >
      {bottomNavItems.map((item) => {
        const Icon = item.icon;
        const isActive = isRouteActive(pathname, item.href);

        if (item.isAction) {
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                'flex min-h-[44px] min-w-[44px] flex-col items-center justify-center gap-0.5',
                'text-white'
              )}
              aria-label={item.label}
            >
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary shadow-lg">
                <Icon className="h-5 w-5" />
              </span>
            </Link>
          );
        }

        return (
          <Link
            key={item.label}
            href={item.href}
            className={cn(
              'relative flex min-h-[44px] min-w-[44px] flex-col items-center justify-center gap-0.5 px-1 text-xs transition-colors',
              isActive ? 'text-primary dark:text-primary' : 'text-gray-500 dark:text-gray-400'
            )}
            aria-current={isActive ? 'page' : undefined}
          >
            <Icon className="h-5 w-5" />
            <span className="text-[10px] font-medium leading-tight">{item.label}</span>
            {item.badge != null && item.badge > 0 && (
              <span className="absolute right-0 top-0.5 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-red-500 px-1 text-[9px] font-bold text-white">
                {item.badge > 99 ? '99+' : item.badge}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
