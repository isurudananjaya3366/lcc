'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { LogOut, Settings, User, ChevronDown } from 'lucide-react';
import { useAuthStore } from '@/stores/useAuthStore';
import { cn } from '@/lib/cn';
import { UserAvatar } from './UserAvatar';

export function UserMenu() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const handleLogout = useCallback(() => {
    setIsOpen(false);
    logout();
    router.replace('/login');
  }, [logout, router]);

  const menuItems = [
    {
      icon: User,
      label: 'Profile',
      onClick: () => {
        router.push('/settings/profile');
        setIsOpen(false);
      },
    },
    {
      icon: Settings,
      label: 'Settings',
      onClick: () => {
        router.push('/settings');
        setIsOpen(false);
      },
    },
  ];

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          'flex items-center gap-2 rounded-lg p-1.5 transition-colors',
          'hover:bg-gray-100 dark:hover:bg-gray-700',
          isOpen && 'bg-gray-100 dark:bg-gray-700',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
        )}
        aria-label="User menu"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <UserAvatar name={user?.first_name} email={user?.email} size="sm" />
        <span className="hidden max-w-[100px] truncate text-sm font-medium text-gray-700 dark:text-gray-300 lg:inline">
          {user?.first_name ?? 'User'}
        </span>
        <ChevronDown
          className={cn(
            'hidden h-3.5 w-3.5 text-gray-400 transition-transform lg:inline',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} aria-hidden="true" />
          <div
            className="absolute right-0 top-12 z-50 w-56 rounded-xl border bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800"
            role="menu"
          >
            {/* User info */}
            <div className="border-b px-4 py-3 dark:border-gray-700">
              <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="truncate text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
            </div>

            {/* Menu items */}
            {menuItems.map(({ icon: Icon, label, onClick }) => (
              <button
                key={label}
                type="button"
                role="menuitem"
                onClick={onClick}
                className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}

            {/* Logout */}
            <div className="border-t dark:border-gray-700">
              <button
                type="button"
                role="menuitem"
                onClick={handleLogout}
                className="flex w-full items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
