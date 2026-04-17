import type { ReactNode } from 'react';

export default function ProductDetailLayout({ children }: { children: ReactNode }) {
  return (
    <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <article>{children}</article>
    </main>
  );
}
