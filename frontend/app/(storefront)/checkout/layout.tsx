import type { Metadata } from 'next';
import { CheckoutHeader } from '@/components/storefront/checkout';
import { Lock, ShieldCheck } from 'lucide-react';
import { CheckoutSidebarWrapper } from './CheckoutSidebarWrapper';

export const metadata: Metadata = {
  title: 'Checkout | LankaCom',
  description: 'Complete your purchase securely.',
  robots: { index: false, follow: false },
};

export default function CheckoutLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <CheckoutHeader />

      <main className="flex-1">
        <div className="container mx-auto max-w-7xl px-4 py-8">
          <CheckoutSidebarWrapper>{children}</CheckoutSidebarWrapper>
        </div>
      </main>

      <footer className="border-t bg-white py-4">
        <div className="container mx-auto flex max-w-7xl items-center justify-center gap-6 px-4 text-xs text-gray-500">
          <span className="inline-flex items-center gap-1">
            <Lock className="h-3.5 w-3.5" />
            SSL Encrypted
          </span>
          <span className="inline-flex items-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5" />
            Secure Payment
          </span>
        </div>
      </footer>
    </div>
  );
}
