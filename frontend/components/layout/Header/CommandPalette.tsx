'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Command } from 'cmdk';
import {
  LayoutDashboard,
  Package,
  ShoppingCart,
  Receipt,
  Users,
  Settings,
  BarChart3,
  Plus,
  FileText,
  Download,
  Search,
  Clock,
  type LucideIcon,
} from 'lucide-react';
import { cn } from '@/lib/cn';

interface CommandPaletteProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

interface CommandItem {
  id: string;
  label: string;
  icon: LucideIcon;
  keywords?: string;
  onSelect: () => void;
}

const RECENT_KEY = 'lcc_recent_pages';
const MAX_RECENT = 5;

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');

  // Reset query when opening
  useEffect(() => {
    if (open) setQuery('');
  }, [open]);

  const navigate = useCallback(
    (path: string) => {
      // Save to recent
      try {
        const recent: string[] = JSON.parse(localStorage.getItem(RECENT_KEY) ?? '[]');
        const updated = [path, ...recent.filter((p) => p !== path)].slice(0, MAX_RECENT);
        localStorage.setItem(RECENT_KEY, JSON.stringify(updated));
      } catch {
        /* ignore */
      }

      router.push(path);
      onOpenChange(false);
    },
    [router, onOpenChange]
  );

  const navigationItems: CommandItem[] = useMemo(
    () => [
      {
        id: 'nav-dashboard',
        label: 'Dashboard',
        icon: LayoutDashboard,
        keywords: 'home overview',
        onSelect: () => navigate('/dashboard'),
      },
      {
        id: 'nav-products',
        label: 'Products',
        icon: Package,
        keywords: 'inventory items',
        onSelect: () => navigate('/inventory/products'),
      },
      {
        id: 'nav-orders',
        label: 'Sales Orders',
        icon: ShoppingCart,
        keywords: 'sales orders',
        onSelect: () => navigate('/sales/orders'),
      },
      {
        id: 'nav-invoices',
        label: 'Invoices',
        icon: FileText,
        keywords: 'billing invoice',
        onSelect: () => navigate('/sales/invoices'),
      },
      {
        id: 'nav-customers',
        label: 'Customers',
        icon: Users,
        keywords: 'clients contacts',
        onSelect: () => navigate('/sales/customers'),
      },
      {
        id: 'nav-accounting',
        label: 'Accounting',
        icon: Receipt,
        keywords: 'finance ledger',
        onSelect: () => navigate('/accounting'),
      },
      {
        id: 'nav-reports',
        label: 'Reports',
        icon: BarChart3,
        keywords: 'analytics data',
        onSelect: () => navigate('/reports'),
      },
      {
        id: 'nav-settings',
        label: 'Settings',
        icon: Settings,
        keywords: 'preferences config',
        onSelect: () => navigate('/settings'),
      },
    ],
    [navigate]
  );

  const quickActions: CommandItem[] = useMemo(
    () => [
      {
        id: 'act-new-product',
        label: 'Create Product',
        icon: Plus,
        keywords: 'new add product',
        onSelect: () => navigate('/inventory/products/new'),
      },
      {
        id: 'act-new-order',
        label: 'Create Sales Order',
        icon: Plus,
        keywords: 'new add order sale',
        onSelect: () => navigate('/sales/orders/new'),
      },
      {
        id: 'act-new-invoice',
        label: 'Create Invoice',
        icon: Plus,
        keywords: 'new add invoice bill',
        onSelect: () => navigate('/sales/invoices/new'),
      },
      {
        id: 'act-export',
        label: 'Export Report',
        icon: Download,
        keywords: 'download export csv',
        onSelect: () => navigate('/reports/export'),
      },
    ],
    [navigate]
  );

  const recentPaths = useMemo(() => {
    if (!open) return [];
    try {
      return JSON.parse(localStorage.getItem(RECENT_KEY) ?? '[]') as string[];
    } catch {
      return [];
    }
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50" role="dialog" aria-modal="true">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 animate-in fade-in-0"
        onClick={() => onOpenChange(false)}
        aria-hidden="true"
      />

      {/* Palette */}
      <div className="fixed left-1/2 top-[20%] w-full max-w-[640px] -translate-x-1/2">
        <Command
          className="overflow-hidden rounded-xl border bg-white shadow-2xl dark:border-gray-700 dark:bg-gray-800"
          label="Command palette"
          shouldFilter
        >
          <div className="flex items-center gap-2 border-b px-4 dark:border-gray-700">
            <Search className="h-4 w-4 shrink-0 text-gray-400" />
            <Command.Input
              value={query}
              onValueChange={setQuery}
              placeholder="Type a command or search..."
              className="flex-1 bg-transparent py-3 text-sm outline-none placeholder:text-gray-500 dark:text-gray-100"
            />
            <kbd className="rounded border border-gray-300 bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500 dark:border-gray-600 dark:bg-gray-700">
              ESC
            </kbd>
          </div>

          <Command.List className="max-h-[60vh] overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-gray-500">
              No results found. Try different keywords.
            </Command.Empty>

            {/* Recent */}
            {recentPaths.length > 0 && (
              <Command.Group heading="Recent">
                {recentPaths.map((path) => (
                  <Command.Item
                    key={`recent-${path}`}
                    value={`recent ${path}`}
                    onSelect={() => navigate(path)}
                    className={cn(
                      'flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 text-sm',
                      'aria-selected:bg-gray-100 dark:aria-selected:bg-gray-700'
                    )}
                  >
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-700 dark:text-gray-300">{path}</span>
                  </Command.Item>
                ))}
              </Command.Group>
            )}

            {/* Navigation */}
            <Command.Group heading="Navigation">
              {navigationItems.map((item) => (
                <Command.Item
                  key={item.id}
                  value={`${item.label} ${item.keywords ?? ''}`}
                  onSelect={item.onSelect}
                  className={cn(
                    'flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 text-sm',
                    'aria-selected:bg-gray-100 dark:aria-selected:bg-gray-700'
                  )}
                >
                  <item.icon className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">{item.label}</span>
                </Command.Item>
              ))}
            </Command.Group>

            {/* Quick Actions */}
            <Command.Group heading="Quick Actions">
              {quickActions.map((item) => (
                <Command.Item
                  key={item.id}
                  value={`${item.label} ${item.keywords ?? ''}`}
                  onSelect={item.onSelect}
                  className={cn(
                    'flex cursor-pointer items-center gap-3 rounded-md px-3 py-2 text-sm',
                    'aria-selected:bg-gray-100 dark:aria-selected:bg-gray-700'
                  )}
                >
                  <item.icon className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">{item.label}</span>
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>
        </Command>
      </div>
    </div>
  );
}
