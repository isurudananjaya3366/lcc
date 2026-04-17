import { cn } from '@/lib/utils';

interface OutOfStockAlertProps {
  itemName: string;
}

export function OutOfStockAlert({ itemName }: OutOfStockAlertProps) {
  return (
    <div
      role="alert"
      aria-label={`${itemName} is no longer available`}
      className={cn(
        'flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2',
        'dark:border-red-800 dark:bg-red-950'
      )}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        className="h-5 w-5 flex-shrink-0 text-red-600 dark:text-red-400"
        aria-hidden="true"
      >
        <path
          fillRule="evenodd"
          d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495ZM10 5a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 10 5Zm0 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"
          clipRule="evenodd"
        />
      </svg>
      <p className="text-sm font-medium text-red-700 dark:text-red-300">
        This item is no longer available
      </p>
    </div>
  );
}
