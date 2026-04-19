import { cn } from '@/lib/utils';

interface PageSidebarProps {
  children: React.ReactNode;
  className?: string;
}

export function PageSidebar({ children, className }: PageSidebarProps) {
  return (
    <aside
      className={cn(
        'hidden lg:block sticky top-24 self-start',
        className,
      )}
    >
      {children}
    </aside>
  );
}
