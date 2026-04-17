'use client';

import React, { useState, type FC } from 'react';
import Link from 'next/link';
import { CartIconButton } from '@/components/storefront/cart/MiniCart';

export interface StoreHeaderProps {
  transparent?: boolean;
  sticky?: boolean;
  hideSearch?: boolean;
  className?: string;
}

/**
 * Main storefront header — logo, navigation, search, and action buttons.
 * Responsive: mobile hamburger, desktop full layout.
 */
const StoreHeader: FC<StoreHeaderProps> = ({
  transparent = false,
  sticky = true,
  hideSearch = false,
  className = '',
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const bgClasses = transparent
    ? 'bg-transparent'
    : 'bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm';

  const positionClasses = sticky ? 'sticky top-0 z-20' : 'relative';

  return (
    <header className={`${positionClasses} ${bgClasses} ${className}`}>
      {/* Announcement bar */}
      <div className="bg-green-700 text-white text-center py-1.5 text-sm font-medium">
        Free delivery on orders over Rs. 5,000 🚚
      </div>

      {/* Main header */}
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 shrink-0">
            <span className="text-xl md:text-2xl font-bold text-green-700 dark:text-green-400">
              Lanka<span className="text-gray-900 dark:text-white">Commerce</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav aria-label="Primary navigation" className="hidden lg:flex items-center gap-6">
            <Link
              href="/"
              className="text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 transition-colors font-medium"
            >
              Home
            </Link>
            <Link
              href="/products"
              className="text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 transition-colors font-medium"
            >
              Shop
            </Link>
            <Link
              href="/search?category=deals"
              className="text-gray-700 dark:text-gray-300 hover:text-green-700 dark:hover:text-green-400 transition-colors font-medium"
            >
              Deals
            </Link>
          </nav>

          {/* Search bar (desktop) */}
          {!hideSearch && (
            <form action="/search" method="GET" className="hidden md:flex flex-1 max-w-md mx-6">
              <div className="relative w-full">
                <input
                  type="search"
                  name="q"
                  placeholder="Search products..."
                  className="w-full rounded-full border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-4 py-2 pl-10 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent dark:text-gray-100"
                  aria-label="Search products"
                />
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
            </form>
          )}

          {/* Action buttons */}
          <div className="flex items-center gap-1 md:gap-2">
            {/* Account */}
            <Link
              href="/account"
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-green-700 dark:hover:text-green-400 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              aria-label="My Account"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
            </Link>

            {/* Wishlist */}
            <Link
              href="/account"
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-green-700 dark:hover:text-green-400 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 relative"
              aria-label="Wishlist"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
            </Link>

            {/* Cart */}
            <CartIconButton />

            {/* Mobile hamburger */}
            <button
              type="button"
              className="lg:hidden p-2 text-gray-600 dark:text-gray-400 hover:text-green-700 dark:hover:text-green-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
              aria-expanded={mobileMenuOpen}
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <nav
          aria-label="Mobile navigation"
          className="lg:hidden bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 px-4 pb-4"
        >
          {/* Mobile search */}
          {!hideSearch && (
            <form action="/search" method="GET" className="mt-3 mb-4">
              <input
                type="search"
                name="q"
                placeholder="Search products..."
                className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 dark:text-gray-100"
                aria-label="Search products"
              />
            </form>
          )}

          <div className="space-y-1">
            <Link
              href="/"
              className="block py-2 text-gray-700 dark:text-gray-300 hover:text-green-700 font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              Home
            </Link>
            <Link
              href="/products"
              className="block py-2 text-gray-700 dark:text-gray-300 hover:text-green-700 font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              Shop
            </Link>
            <Link
              href="/search?category=deals"
              className="block py-2 text-gray-700 dark:text-gray-300 hover:text-green-700 font-medium"
              onClick={() => setMobileMenuOpen(false)}
            >
              Deals
            </Link>
          </div>
        </nav>
      )}
    </header>
  );
};

export default StoreHeader;
