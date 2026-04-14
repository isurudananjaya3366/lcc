'use client';

import { useMemo } from 'react';
import { useAuthStore } from '@/stores/useAuthStore';
import { cn } from '@/lib/cn';

/**
 * Personalized welcome banner with time-based greeting.
 */
export function WelcomeBanner() {
  const user = useAuthStore((s) => s.user);

  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }, []);

  const dateStr = useMemo(() => {
    return new Intl.DateTimeFormat('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date());
  }, []);

  const firstName = user?.first_name || 'User';

  return (
    <div
      className={cn(
        'rounded-xl bg-gradient-to-r from-primary/10 via-primary/5 to-transparent p-6',
        'dark:from-primary/20 dark:via-primary/10 dark:to-transparent'
      )}
    >
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 sm:text-3xl">
        {greeting}, {firstName}
      </h1>
      <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{dateStr}</p>
    </div>
  );
}
