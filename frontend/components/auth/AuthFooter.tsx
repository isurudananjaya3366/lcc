import Link from 'next/link';

import { cn } from '@/lib/cn';

export interface AuthFooterProps {
  className?: string;
}

export function AuthFooter({ className }: AuthFooterProps) {
  return (
    <footer
      className={cn('border-t border-gray-200 pt-4 text-center dark:border-gray-700', className)}
    >
      <nav
        className="mb-2 flex flex-col items-center gap-2 sm:flex-row sm:justify-center sm:gap-4"
        aria-label="Footer links"
      >
        <Link
          href="/help"
          className="text-sm text-gray-600 transition-colors hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
        >
          Help
        </Link>
        <Link
          href="/privacy"
          className="text-sm text-gray-600 transition-colors hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
        >
          Privacy Policy
        </Link>
        <Link
          href="/terms"
          className="text-sm text-gray-600 transition-colors hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
        >
          Terms of Service
        </Link>
      </nav>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        &copy; {new Date().getFullYear()} LankaCommerce Cloud. All rights reserved.
      </p>
    </footer>
  );
}
