'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, Package, ShoppingCart, FileText, Users } from 'lucide-react';
import { cn } from '@/lib/cn';

const actions = [
  { icon: Package, label: 'New Product', href: '/inventory/products/new' },
  { icon: ShoppingCart, label: 'New Order', href: '/sales/orders/new' },
  { icon: FileText, label: 'New Invoice', href: '/sales/invoices/new' },
  { icon: Users, label: 'New Customer', href: '/sales/customers/new' },
];

export function QuickActions() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={cn(
          'hidden h-10 w-10 items-center justify-center rounded-lg text-gray-600 transition-colors lg:flex',
          'hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700',
          isOpen && 'bg-gray-100 dark:bg-gray-700',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
        )}
        aria-label="Quick actions"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <Plus className="h-5 w-5" />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} aria-hidden="true" />
          <div
            className="absolute right-0 top-12 z-50 w-48 rounded-lg border bg-white py-1 shadow-lg dark:border-gray-700 dark:bg-gray-800"
            role="menu"
          >
            {actions.map(({ icon: Icon, label, href }) => (
              <button
                key={label}
                type="button"
                role="menuitem"
                onClick={() => {
                  router.push(href);
                  setIsOpen(false);
                }}
                className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
