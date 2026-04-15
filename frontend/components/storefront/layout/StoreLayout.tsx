'use client';

import React, { type ReactNode, type FC } from 'react';

export interface StoreLayoutProps {
  children: ReactNode;
  hideHeader?: boolean;
  hideFooter?: boolean;
  fullWidth?: boolean;
}

/**
 * Main store layout component — wraps all storefront pages.
 * Provides three-section structure: header, main content, footer.
 */
const StoreLayout: FC<StoreLayoutProps> = ({
  children,
  hideHeader = false,
  hideFooter = false,
  fullWidth = false,
}) => {
  return (
    <div className="min-h-screen flex flex-col bg-[var(--store-bg,#ffffff)]">
      {/* Skip navigation for accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-white focus:text-green-700 focus:underline"
      >
        Skip to main content
      </a>

      {/* Header */}
      {!hideHeader && (
        <header className="sticky top-0 z-20 bg-white border-b border-gray-200 shadow-sm">
          {/* StoreHeader will be integrated here later */}
          <div className="container mx-auto px-4 md:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16 md:h-20">
              <span className="text-xl font-bold text-green-700">LankaCommerce</span>
              <nav aria-label="Primary navigation" className="hidden md:flex items-center gap-6">
                <a href="/" className="text-gray-700 hover:text-green-700 transition-colors">
                  Home
                </a>
                <a
                  href="/products"
                  className="text-gray-700 hover:text-green-700 transition-colors"
                >
                  Shop
                </a>
                <a href="/search" className="text-gray-700 hover:text-green-700 transition-colors">
                  Search
                </a>
              </nav>
              <div className="flex items-center gap-3">
                <a
                  href="/account"
                  className="p-2 text-gray-600 hover:text-green-700"
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
                </a>
                <a
                  href="/cart"
                  className="p-2 text-gray-600 hover:text-green-700 relative"
                  aria-label="Shopping Cart"
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
                      d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z"
                    />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Main content */}
      <main id="main-content" role="main" className="flex-1">
        {fullWidth ? (
          children
        ) : (
          <div className="container mx-auto px-4 md:px-6 lg:px-8">{children}</div>
        )}
      </main>

      {/* Footer */}
      {!hideFooter && (
        <footer className="mt-auto bg-gray-900 text-gray-300">
          {/* StoreFooter will be integrated here later */}
          <div className="container mx-auto px-4 md:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div>
                <h3 className="text-white text-lg font-semibold mb-4">Shop</h3>
                <ul className="space-y-2 text-sm">
                  <li>
                    <a href="/products" className="hover:text-white transition-colors">
                      All Products
                    </a>
                  </li>
                  <li>
                    <a href="/search" className="hover:text-white transition-colors">
                      Search
                    </a>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-white text-lg font-semibold mb-4">Customer Service</h3>
                <ul className="space-y-2 text-sm">
                  <li>
                    <a href="/help" className="hover:text-white transition-colors">
                      Help Center
                    </a>
                  </li>
                  <li>
                    <a href="/contact" className="hover:text-white transition-colors">
                      Contact Us
                    </a>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-white text-lg font-semibold mb-4">Company</h3>
                <ul className="space-y-2 text-sm">
                  <li>
                    <a href="/about" className="hover:text-white transition-colors">
                      About Us
                    </a>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="text-white text-lg font-semibold mb-4">Connect</h3>
                <p className="text-sm">
                  Follow us on social media for updates and exclusive offers.
                </p>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800">
            <div className="container mx-auto px-4 md:px-6 lg:px-8 py-6">
              <p className="text-sm text-center text-gray-500">
                &copy; {new Date().getFullYear()} LankaCommerce Cloud. All rights reserved.
              </p>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
};

export default StoreLayout;
