import type { ReactNode } from 'react';

interface ProductLayoutProps {
  gallery: ReactNode;
  info: ReactNode;
  className?: string;
}

export function ProductLayout({ gallery, info, className }: ProductLayoutProps) {
  return (
    <div className={className}>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 lg:gap-12">
        {/* Gallery column */}
        <div className="w-full">{gallery}</div>
        {/* Info column */}
        <div className="w-full">{info}</div>
      </div>
    </div>
  );
}
