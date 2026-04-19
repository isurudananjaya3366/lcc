import { cn } from '@/lib/utils';

interface PageLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function PageLayout({ children, className }: PageLayoutProps) {
  return (
    <div className={cn('max-w-4xl mx-auto py-8 px-4', className)}>
      {children}
    </div>
  );
}
