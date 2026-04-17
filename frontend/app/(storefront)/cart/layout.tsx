import type { ReactNode } from 'react';

export default function CartLayout({ children }: { children: ReactNode }) {
  return (
    <div className="container mx-auto max-w-5xl px-4 py-8">
      {children}
    </div>
  );
}
