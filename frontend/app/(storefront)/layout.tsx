import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import { storeFontClassNames } from './fonts';
import '@/styles/store.css';
import StoreProviders from '@/components/storefront/providers/StoreProviders';
import StoreHeader from '@/components/storefront/layout/StoreHeader';
import StoreFooter from '@/components/storefront/layout/StoreFooter';

export const metadata: Metadata = {
  title: {
    template: '%s - LankaCommerce Store',
    default: 'LankaCommerce Store',
  },
  description:
    'Shop quality products with seamless checkout. Free delivery across Sri Lanka on orders over Rs. 5,000.',
  keywords: ['sri lanka', 'online shopping', 'e-commerce', 'pos', 'lankacommerce'],
  openGraph: {
    type: 'website',
    locale: 'en_LK',
    siteName: 'LankaCommerce Store',
    title: 'LankaCommerce Store',
    description: 'Shop quality products with seamless checkout. Free delivery across Sri Lanka.',
  },
  twitter: {
    card: 'summary_large_image',
  },
};

/**
 * Storefront route-group layout.
 *
 * Customer-facing e-commerce layout with:
 *  - StoreHeader (navigation, search, cart, account)
 *  - Main content area (children)
 *  - StoreFooter (links, info, social)
 *  - StoreProviders (theme, auth, cart)
 */
export default function StorefrontLayout({ children }: { children: ReactNode }) {
  return (
    <div className={`min-h-screen flex flex-col bg-gray-50 ${storeFontClassNames}`}>
      <StoreProviders>
        <StoreHeader />
        <main className="flex-grow">{children}</main>
        <StoreFooter />
      </StoreProviders>
    </div>
  );
}
