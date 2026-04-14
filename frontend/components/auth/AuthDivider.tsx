import { cn } from '@/lib/cn';

export interface AuthDividerProps {
  text?: string;
  className?: string;
}

export function AuthDivider({ text = 'or', className }: AuthDividerProps) {
  return (
    <div className={cn('my-6 flex items-center', className)}>
      <div className="flex-grow border-t border-gray-300 dark:border-gray-700" />
      <span className="px-4 text-sm text-gray-500 dark:text-gray-400">{text}</span>
      <div className="flex-grow border-t border-gray-300 dark:border-gray-700" />
    </div>
  );
}
