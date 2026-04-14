'use client';

import { useState } from 'react';
import { Building2, ChevronDown, Check } from 'lucide-react';
import { useAuthStore } from '@/stores/useAuthStore';
import { cn } from '@/lib/cn';

interface Tenant {
  id: string;
  name: string;
}

// Placeholder tenants — will be replaced with real data
const MOCK_TENANTS: Tenant[] = [
  { id: '1', name: 'LankaCommerce HQ' },
  { id: '2', name: 'Colombo Branch' },
  { id: '3', name: 'Kandy Branch' },
];

export function TenantSwitcher() {
  const [isOpen, setIsOpen] = useState(false);
  const tenant = useAuthStore((s) => s.tenant);
  const currentId = tenant?.id?.toString() ?? '1';

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          'hidden items-center gap-2 rounded-lg border border-gray-200 px-3 py-1.5 text-sm transition-colors lg:flex',
          'hover:bg-gray-100 dark:border-gray-600 dark:hover:bg-gray-700',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
        )}
        aria-label="Switch tenant"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <Building2 className="h-4 w-4 text-gray-500" />
        <span className="max-w-[120px] truncate text-gray-700 dark:text-gray-300">
          {tenant?.name ?? 'LankaCommerce HQ'}
        </span>
        <ChevronDown
          className={cn('h-3.5 w-3.5 text-gray-400 transition-transform', isOpen && 'rotate-180')}
        />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} aria-hidden="true" />
          <div
            className="absolute right-0 top-10 z-50 w-56 rounded-lg border bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800"
            role="listbox"
            aria-label="Tenants"
          >
            {MOCK_TENANTS.map((t) => (
              <button
                key={t.id}
                type="button"
                role="option"
                aria-selected={t.id === currentId}
                onClick={() => {
                  // TODO: call tenant switch API
                  setIsOpen(false);
                }}
                className={cn(
                  'flex w-full items-center justify-between px-4 py-2 text-sm transition-colors',
                  'hover:bg-gray-100 dark:hover:bg-gray-700',
                  t.id === currentId
                    ? 'font-medium text-primary'
                    : 'text-gray-700 dark:text-gray-300'
                )}
              >
                <span className="truncate">{t.name}</span>
                {t.id === currentId && <Check className="h-4 w-4 shrink-0" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
