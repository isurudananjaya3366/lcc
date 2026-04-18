import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: {
    template: '%s | Account',
    default: 'Account',
  },
  description: 'Customer account area.',
};

export default function AccountLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center bg-muted/40 px-4 py-8">
      {/* Logo */}
      <Link href="/" className="mb-8 text-2xl font-bold tracking-tight">
        Store
      </Link>

      {/* Content card */}
      <div className="w-full max-w-md rounded-lg border bg-card p-6 shadow-sm">
        {children}
      </div>

      {/* Footer links */}
      <footer className="mt-8 flex gap-4 text-sm text-muted-foreground">
        <Link href="/" className="hover:underline">
          Home
        </Link>
        <Link href="/products" className="hover:underline">
          Products
        </Link>
        <Link href="/account" className="hover:underline">
          Account
        </Link>
      </footer>
    </div>
  );
}
