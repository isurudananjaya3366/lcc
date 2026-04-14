'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { MenuItem } from '@/config/navigation-menu';
import { isRouteActive } from '@/lib/navigation';
import { cn } from '@/lib/cn';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface NavItemProps {
  item: MenuItem;
  isCollapsed: boolean;
  depth?: number;
}

export function NavItem({ item, isCollapsed, depth = 0 }: NavItemProps) {
  const pathname = usePathname();
  const isActive = isRouteActive(pathname, item.path);
  const Icon = item.icon;

  const paddingLeft = isCollapsed ? undefined : 12 + depth * 12;

  const content = (
    <Link
      href={item.path ?? '#'}
      className={cn(
        'group relative flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
        isCollapsed && 'justify-center px-2',
        isActive
          ? 'bg-primary/10 font-medium text-primary'
          : 'text-gray-300 hover:bg-slate-800 hover:text-white',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
      )}
      style={paddingLeft ? { paddingLeft } : undefined}
      aria-current={isActive ? 'page' : undefined}
      role="menuitem"
      aria-label={item.label}
    >
      {/* Active indicator */}
      {isActive && <span className="absolute inset-y-1 left-0 w-1 rounded-r-full bg-primary" />}

      <Icon
        className={cn('shrink-0 transition-all duration-250', isCollapsed ? 'h-6 w-6' : 'h-5 w-5')}
      />

      {!isCollapsed && (
        <span className="truncate transition-opacity duration-200">{item.label}</span>
      )}

      {!isCollapsed && item.badge != null && (
        <span className="ml-auto rounded-full bg-primary/20 px-2 py-0.5 text-xs font-medium text-primary">
          {item.badge}
        </span>
      )}
    </Link>
  );

  if (isCollapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{content}</TooltipTrigger>
        <TooltipContent side="right" sideOffset={8}>
          {item.label}
        </TooltipContent>
      </Tooltip>
    );
  }

  return content;
}
