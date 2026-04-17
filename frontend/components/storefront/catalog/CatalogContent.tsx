import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CatalogContentProps {
  sidebar: ReactNode;
  children: ReactNode;
  className?: string;
}

export function CatalogContent({ sidebar, children, className }: CatalogContentProps) {
  return (
    <div className={cn('grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 lg:gap-8', className)}>
      <aside className="hidden lg:block">{sidebar}</aside>
      <main>{children}</main>
    </div>
  );
}
