import { cn } from '@/lib/cn';

export interface AuthHeadingProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export function AuthHeading({ title, subtitle, className }: AuthHeadingProps) {
  return (
    <div className={cn('mb-6 text-center', className)}>
      <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 md:text-3xl">{title}</h1>
      {subtitle && <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{subtitle}</p>}
    </div>
  );
}
