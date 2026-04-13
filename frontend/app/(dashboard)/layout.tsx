import type { ReactNode } from 'react';
import Link from 'next/link';

/**
 * Navigation items for the dashboard sidebar.
 */
const navItems = [
  { label: 'Dashboard', href: '/dashboard', icon: '📊' },
  { label: 'Inventory', href: '/inventory', icon: '📦' },
  { label: 'Sales', href: '/sales', icon: '💰' },
  { label: 'Purchasing', href: '/purchasing', icon: '🛒' },
  { label: 'Accounting', href: '/accounting', icon: '📒' },
  { label: 'Reports', href: '/reports', icon: '📈' },
  { label: 'Settings', href: '/settings', icon: '⚙️' },
];

/**
 * Dashboard layout with sidebar navigation and header.
 * All protected ERP pages render inside this layout.
 */
export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      {/* Skip to main content */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-blue-600 focus:px-4 focus:py-2 focus:text-white"
      >
        Skip to main content
      </a>

      {/* Sidebar */}
      <aside className="flex w-60 flex-col bg-slate-900 text-gray-100" aria-label="Main navigation sidebar">
        {/* Logo */}
        <div className="flex h-16 items-center px-6">
          <span className="text-lg font-bold">LankaCommerce</span>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4" aria-label="Dashboard navigation">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-300 hover:bg-slate-800 hover:text-white"
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-slate-700 px-4 py-3">
          <p className="truncate text-sm text-gray-400">Signed in</p>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b bg-white px-6">
          <h2 className="text-lg font-semibold text-gray-900">Dashboard</h2>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">🔔</span>
            <span className="text-sm text-gray-500">👤</span>
          </div>
        </header>

        {/* Breadcrumbs */}
        <div className="border-b bg-white px-6 py-2 text-sm text-gray-500">
          Home
        </div>

        {/* Page Content */}
        <main id="main-content" className="flex-1 bg-gray-50 p-6">{children}</main>
      </div>
    </div>
  );
}
