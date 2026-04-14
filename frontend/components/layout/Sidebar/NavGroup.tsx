'use client';

import { useCallback, useEffect, useId, useState } from 'react';
import { usePathname } from 'next/navigation';
import { ChevronDown } from 'lucide-react';
import type { MenuItem } from '@/config/navigation-menu';
import { isMenuItemActive } from '@/lib/navigation';
import { cn } from '@/lib/cn';
import { NavItem } from './NavItem';
import { SubNavItem } from './SubNavItem';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface NavGroupProps {
  item: MenuItem;
  isCollapsed: boolean;
  depth?: number;
}

export function NavGroup({ item, isCollapsed, depth = 0 }: NavGroupProps) {
  const pathname = usePathname();
  const childActive = isMenuItemActive(pathname, item);
  const [isExpanded, setIsExpanded] = useState(childActive);
  const groupId = useId();

  const Icon = item.icon;
  const children = item.children ?? [];

  // Auto-expand when a child becomes active
  useEffect(() => {
    if (childActive) setIsExpanded(true);
  }, [childActive]);

  const toggle = useCallback(() => {
    setIsExpanded((prev) => !prev);
  }, []);

  // Collapsed mode — show only icon with tooltip
  if (isCollapsed) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            onClick={toggle}
            className={cn(
              'flex w-full items-center justify-center rounded-md px-2 py-2 transition-colors',
              childActive
                ? 'bg-primary/10 text-primary'
                : 'text-gray-300 hover:bg-slate-800 hover:text-white',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
            )}
            aria-label={item.label}
            role="menuitem"
          >
            <Icon className="h-6 w-6" />
          </button>
        </TooltipTrigger>
        <TooltipContent side="right" sideOffset={8} className="space-y-1 p-2">
          <p className="font-medium">{item.label}</p>
          {children.map((child) => (
            <SubNavItem
              key={child.id}
              href={child.path ?? '#'}
              label={child.label}
              icon={child.icon}
              isCollapsed={false}
            />
          ))}
        </TooltipContent>
      </Tooltip>
    );
  }

  return (
    <div>
      {/* Group header */}
      <button
        type="button"
        onClick={toggle}
        className={cn(
          'group flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
          childActive
            ? 'bg-accent/5 font-medium text-gray-100'
            : 'text-gray-300 hover:bg-slate-800 hover:text-white',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
        )}
        style={{ paddingLeft: 12 + depth * 12 }}
        aria-expanded={isExpanded}
        aria-controls={groupId}
        role="menuitem"
      >
        <Icon className="h-5 w-5 shrink-0" />
        <span className="flex-1 truncate text-left">{item.label}</span>
        <ChevronDown
          className={cn(
            'h-4 w-4 shrink-0 text-gray-500 transition-transform duration-200',
            isExpanded && 'rotate-180'
          )}
        />
      </button>

      {/* Children */}
      <div
        id={groupId}
        className={cn(
          'overflow-hidden transition-[max-height] duration-300 ease-in-out',
          isExpanded ? 'max-h-96' : 'max-h-0'
        )}
        role="menu"
      >
        <div className="space-y-0.5 py-1">
          {children.map((child) =>
            child.children ? (
              <NavGroup key={child.id} item={child} isCollapsed={false} depth={depth + 1} />
            ) : (
              <SubNavItem
                key={child.id}
                href={child.path ?? '#'}
                label={child.label}
                icon={child.icon}
                isCollapsed={false}
              />
            )
          )}
        </div>
      </div>
    </div>
  );
}
