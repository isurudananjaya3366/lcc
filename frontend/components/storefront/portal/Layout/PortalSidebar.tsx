'use client';

import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Package,
  MapPin,
  Heart,
  Star,
  Settings,
} from 'lucide-react';
import { LogoutButton } from '@/components/storefront/auth/LogoutButton';
import { SidebarNavItem } from './SidebarNavItem';

const navItems = [
  { href: '/account/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/account/orders', icon: Package, label: 'Orders' },
  { href: '/account/addresses', icon: MapPin, label: 'Addresses' },
  { href: '/account/wishlist', icon: Heart, label: 'Wishlist' },
  { href: '/account/reviews', icon: Star, label: 'Reviews' },
  { href: '/account/settings', icon: Settings, label: 'Settings' },
];

export interface PortalSidebarProps {
  onNavigate?: () => void;
}

export function PortalSidebar({ onNavigate }: PortalSidebarProps) {
  const pathname = usePathname();

  return (
    <nav className="flex h-full flex-col gap-1 p-4">
      {navItems.map((item) => (
        <SidebarNavItem
          key={item.href}
          href={item.href}
          icon={item.icon}
          label={item.label}
          isActive={pathname === item.href || pathname.startsWith(item.href + '/')}
          onClick={onNavigate}
        />
      ))}
      <div className="mt-auto pt-4 border-t">
        <LogoutButton variant="ghost" className="w-full justify-start gap-3 px-3 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground" />
      </div>
    </nav>
  );
}
