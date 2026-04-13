import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#3b82f6',
};

export const metadata: Metadata = {
  title: {
    default: 'LankaCommerce Cloud',
    template: '%s | LankaCommerce Cloud',
  },
  description:
    'Multi-tenant ERP system for Sri Lankan SMEs — inventory, POS, accounting, and e-commerce platform.',
  keywords: [
    'ERP',
    'POS',
    'inventory',
    'multi-tenant',
    'Sri Lanka',
    'accounting',
    'sales',
  ],
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  openGraph: {
    type: 'website',
    locale: 'en_LK',
    siteName: 'LankaCommerce Cloud',
  },
  twitter: {
    card: 'summary_large_image',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-LK" className={inter.variable}>
      <body className={`${inter.className} antialiased`}>
        {/* Future providers (theme, auth, store) will wrap children here */}
        {children}
        <Toaster />
      </body>
    </html>
  );
}
