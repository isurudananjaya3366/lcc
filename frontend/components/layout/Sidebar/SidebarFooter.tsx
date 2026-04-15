'use client';

import { useRouter } from 'next/navigation';
import { useCallback } from 'react';
import { LogOut, Settings, Sliders, UserCircle } from 'lucide-react';
import { useAuthStore } from '@/stores/useAuthStore';
import { cn } from '@/lib/cn';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';

interface SidebarFooterProps {
  isCollapsed: boolean;
}

export function SidebarFooter({ isCollapsed }: SidebarFooterProps) {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = useCallback(() => {
    logout();
    router.replace('/login');
  }, [logout, router]);

  const avatar = (
    <div
      className={cn(
        'flex shrink-0 items-center justify-center rounded-full bg-slate-600 font-medium text-white',
        isCollapsed ? 'h-8 w-8 text-xs' : 'h-10 w-10 text-sm'
      )}
      aria-hidden="true"
    >
      {user?.firstName?.[0]?.toUpperCase() ?? user?.email?.[0]?.toUpperCase() ?? 'U'}
    </div>
  );

  if (isCollapsed) {
    return (
      <div className="border-t border-slate-700 p-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              className="mx-auto flex items-center justify-center rounded-md p-1 hover:bg-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label={user?.email ?? 'User menu'}
            >
              {avatar}
            </button>
          </TooltipTrigger>
          <TooltipContent side="right" sideOffset={8} className="space-y-1 p-2">
            <p className="font-medium">{user?.firstName ?? 'User'}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
            <hr className="my-1 border-border" />
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded px-2 py-1 text-sm text-destructive hover:bg-destructive/10"
            >
              <LogOut className="h-4 w-4" /> Logout
            </button>
          </TooltipContent>
        </Tooltip>
      </div>
    );
  }

  return (
    <div className="border-t border-slate-700 px-4 py-3">
      <div className="flex items-center gap-3">
        {avatar}
        <div className="flex-1 overflow-hidden">
          <p className="truncate text-sm font-medium text-gray-100">{user?.firstName ?? 'User'}</p>
          <p className="truncate text-xs text-gray-400">{user?.email}</p>
        </div>
      </div>

      {/* Quick actions */}
      <div className="mt-2 flex gap-1">
        <FooterAction icon={UserCircle} label="Profile" href="/settings/profile" />
        <FooterAction icon={Settings} label="Settings" href="/settings" />
        <FooterAction icon={Sliders} label="Preferences" href="/settings/preferences" />
        <button
          type="button"
          onClick={handleLogout}
          className="flex h-8 w-8 items-center justify-center rounded-md text-gray-400 hover:bg-slate-700 hover:text-red-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          aria-label="Logout"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

function FooterAction({
  icon: Icon,
  label,
  href,
}: {
  icon: typeof UserCircle;
  label: string;
  href: string;
}) {
  return (
    <a
      href={href}
      className="flex h-8 w-8 items-center justify-center rounded-md text-gray-400 hover:bg-slate-700 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
      aria-label={label}
    >
      <Icon className="h-4 w-4" />
    </a>
  );
}
