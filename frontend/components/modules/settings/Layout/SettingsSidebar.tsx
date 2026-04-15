'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Settings, Building2, Users, Shield, Link2, Key, CreditCard, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}

const accountItems: NavItem[] = [
  { label: 'General Settings', href: '/settings', icon: Settings },
  { label: 'Company Profile', href: '/settings/company', icon: Building2 },
  { label: 'User Management', href: '/settings/users', icon: Users },
  { label: 'Roles & Permissions', href: '/settings/roles', icon: Shield },
];

const systemItems: NavItem[] = [
  { label: 'Integrations', href: '/settings/integrations', icon: Link2 },
  { label: 'API Keys', href: '/settings/api-keys', icon: Key },
  { label: 'Billing & Plans', href: '/settings/billing', icon: CreditCard },
  { label: 'Audit Log', href: '/settings/audit-log', icon: FileText },
];

interface SettingsSidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export function SettingsSidebar({ className, onNavigate }: SettingsSidebarProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/settings') return pathname === '/settings';
    return pathname.startsWith(href);
  };

  const renderNavItem = (item: NavItem) => {
    const active = isActive(item.href);
    const Icon = item.icon;
    return (
      <Link
        key={item.href}
        href={item.href}
        onClick={onNavigate}
        className={cn(
          'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          active
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
        )}
      >
        <Icon className="h-5 w-5 shrink-0" />
        {item.label}
      </Link>
    );
  };

  return (
    <nav className={cn('space-y-6', className)}>
      <div>
        <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Account
        </h3>
        <div className="space-y-1">{accountItems.map(renderNavItem)}</div>
      </div>
      <div>
        <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          System
        </h3>
        <div className="space-y-1">{systemItems.map(renderNavItem)}</div>
      </div>
    </nav>
  );
}
