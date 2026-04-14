'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { isRouteActive } from '@/lib/navigation';
import { cn } from '@/lib/cn';
import type { LucideIcon } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface SubNavItemProps {
  href: string;
  label: string;
  icon?: LucideIcon;
  isCollapsed: boolean;
}

export function SubNavItem({ href, label, icon: Icon, isCollapsed }: SubNavItemProps) {
  const pathname = usePathname();
  const isActive = isRouteActive(pathname, href);

  // Hidden in collapsed mode — tooltip on parent group handles this
  if (isCollapsed) {
    if (!Icon) return null;
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <Link
            href={href}
            className={cn(
              'flex items-center justify-center rounded-md px-2 py-1.5 transition-colors',
              isActive
                ? 'bg-primary/10 text-primary'
                : 'text-gray-400 hover:bg-slate-800 hover:text-white',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
            )}
            aria-current={isActive ? 'page' : undefined}
            role="menuitem"
            aria-label={label}
          >
            <Icon className="h-4 w-4" />
          </Link>
        </TooltipTrigger>
        <TooltipContent side="right" sideOffset={8}>
          {label}
        </TooltipContent>
      </Tooltip>
    );
  }

  return (
    <Link
      href={href}
      className={cn(
        'group relative flex items-center gap-2 rounded-md py-1.5 pl-12 pr-3 text-sm transition-colors',
        isActive
          ? 'bg-primary/10 font-medium text-primary'
          : 'text-gray-400 hover:bg-slate-800 hover:text-white',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
      )}
      aria-current={isActive ? 'page' : undefined}
      role="menuitem"
      aria-label={label}
    >
      {isActive && <span className="absolute inset-y-1 left-0 w-1 rounded-r-full bg-primary" />}
      {Icon && <Icon className="h-4 w-4 shrink-0" />}
      <span className="truncate">{label}</span>
    </Link>
  );
}
