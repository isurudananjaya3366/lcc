import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: {
    default: 'LankaCommerce Cloud',
    template: '%s | LankaCommerce',
  },
  description: 'Multi-tenant ERP platform for Sri Lankan SMEs',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        {/* Future providers (theme, auth, store) will wrap children here */}
        {children}
      </body>
    </html>
  );
}
