'use client';

import { useCallback } from 'react';
import { Monitor, Moon, Sun } from 'lucide-react';
import { useUIStore } from '@/stores/useUIStore';
import type { ThemeMode } from '@/stores/types';
import { cn } from '@/lib/cn';

const themes: { value: ThemeMode; icon: typeof Sun; label: string }[] = [
  { value: 'light', icon: Sun, label: 'Light' },
  { value: 'dark', icon: Moon, label: 'Dark' },
  { value: 'system', icon: Monitor, label: 'System' },
];

export function ThemeToggle() {
  const theme = useUIStore((s) => s.theme);
  const setTheme = useUIStore((s) => s.setTheme);

  const cycle = useCallback(() => {
    const idx = themes.findIndex((t) => t.value === theme);
    const next = themes[(idx + 1) % themes.length];
    if (next) setTheme(next.value);
  }, [theme, setTheme]);

  const current = themes.find((t) => t.value === theme) ?? themes[0]!;
  const Icon = current.icon;

  return (
    <button
      type="button"
      onClick={cycle}
      className={cn(
        'flex h-10 w-10 items-center justify-center rounded-lg text-gray-600 transition-colors',
        'hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
      )}
      aria-label={`Theme: ${current.label}. Click to change.`}
    >
      <Icon className="h-5 w-5" />
    </button>
  );
}
