'use client';

import { useCallback, useMemo, useRef } from 'react';
import type { MenuItem } from '@/config/navigation-menu';
import { NavItem } from './NavItem';
import { NavGroup } from './NavGroup';

interface SidebarNavProps {
  items: MenuItem[];
  isCollapsed: boolean;
}

export function SidebarNav({ items, isCollapsed }: SidebarNavProps) {
  const navRef = useRef<HTMLElement>(null);

  // Separate items at dividers
  const sections = useMemo(() => {
    const result: MenuItem[][] = [[]];
    for (const item of items) {
      if (item.divider) result.push([]);
      result[result.length - 1].push(item);
    }
    return result;
  }, [items]);

  // Keyboard navigation handler
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const nav = navRef.current;
      if (!nav) return;

      const focusableItems = Array.from(
        nav.querySelectorAll<HTMLElement>(
          'a[role="menuitem"], button[role="menuitem"]'
        )
      );
      const currentIndex = focusableItems.indexOf(
        document.activeElement as HTMLElement
      );

      switch (e.key) {
        case 'ArrowDown': {
          e.preventDefault();
          const next =
            currentIndex < focusableItems.length - 1 ? currentIndex + 1 : 0;
          focusableItems[next]?.focus();
          break;
        }
        case 'ArrowUp': {
          e.preventDefault();
          const prev =
            currentIndex > 0 ? currentIndex - 1 : focusableItems.length - 1;
          focusableItems[prev]?.focus();
          break;
        }
        case 'Home': {
          e.preventDefault();
          focusableItems[0]?.focus();
          break;
        }
        case 'End': {
          e.preventDefault();
          focusableItems[focusableItems.length - 1]?.focus();
          break;
        }
        case 'Escape': {
          e.preventDefault();
          const mainContent = document.getElementById('main-content');
          mainContent?.focus();
          break;
        }
      }
    },
    []
  );

  return (
    <nav
      ref={navRef}
      className="flex-1 space-y-1 overflow-y-auto overflow-x-hidden px-3 py-4 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-700"
      role="navigation"
      aria-label="Main navigation"
      onKeyDown={handleKeyDown}
    >
      {sections.map((section, i) => (
        <div key={i} className={i > 0 ? 'border-t border-slate-700 pt-3' : undefined} role="menu">
          {section.map((item) =>
            item.children && item.children.length > 0 ? (
              <NavGroup key={item.id} item={item} isCollapsed={isCollapsed} />
            ) : (
              <NavItem key={item.id} item={item} isCollapsed={isCollapsed} />
            )
          )}
        </div>
      ))}
    </nav>
  );
}
