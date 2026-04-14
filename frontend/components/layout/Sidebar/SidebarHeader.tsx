'use client';

import { cn } from '@/lib/cn';
import { Logo } from './Logo';
import { CollapseToggle } from './CollapseToggle';

interface SidebarHeaderProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

export function SidebarHeader({ isCollapsed, onToggle }: SidebarHeaderProps) {
  return (
    <div
      className={cn(
        'flex h-16 shrink-0 items-center border-b border-slate-700',
        isCollapsed ? 'justify-center px-2' : 'justify-between px-4'
      )}
    >
      <Logo isCollapsed={isCollapsed} />
      {!isCollapsed && <CollapseToggle isCollapsed={isCollapsed} onToggle={onToggle} />}
    </div>
  );
}
