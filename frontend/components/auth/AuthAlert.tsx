'use client';

import { AlertCircle, CheckCircle2, Info, AlertTriangle, X } from 'lucide-react';

import { cn } from '@/lib/cn';

export type AuthAlertType = 'success' | 'error' | 'warning' | 'info';

export interface AuthAlertProps {
  type: AuthAlertType;
  message: string;
  onClose?: () => void;
  className?: string;
}

const alertConfig: Record<
  AuthAlertType,
  { icon: typeof CheckCircle2; bg: string; border: string; text: string; iconColor: string }
> = {
  success: {
    icon: CheckCircle2,
    bg: 'bg-green-50 dark:bg-green-950/30',
    border: 'border-green-300 dark:border-green-800',
    text: 'text-green-800 dark:text-green-300',
    iconColor: 'text-green-600 dark:text-green-400',
  },
  error: {
    icon: AlertCircle,
    bg: 'bg-red-50 dark:bg-red-950/30',
    border: 'border-red-300 dark:border-red-800',
    text: 'text-red-800 dark:text-red-300',
    iconColor: 'text-red-600 dark:text-red-400',
  },
  warning: {
    icon: AlertTriangle,
    bg: 'bg-yellow-50 dark:bg-yellow-950/30',
    border: 'border-yellow-300 dark:border-yellow-800',
    text: 'text-yellow-800 dark:text-yellow-300',
    iconColor: 'text-yellow-600 dark:text-yellow-400',
  },
  info: {
    icon: Info,
    bg: 'bg-blue-50 dark:bg-blue-950/30',
    border: 'border-blue-300 dark:border-blue-800',
    text: 'text-blue-800 dark:text-blue-300',
    iconColor: 'text-blue-600 dark:text-blue-400',
  },
};

export function AuthAlert({ type, message, onClose, className }: AuthAlertProps) {
  const config = alertConfig[type];
  const Icon = config.icon;

  return (
    <div
      role="alert"
      aria-live="polite"
      className={cn(
        'flex items-center gap-3 rounded-md border p-4',
        config.bg,
        config.border,
        className
      )}
    >
      <Icon className={cn('h-5 w-5 shrink-0', config.iconColor)} />
      <p className={cn('flex-1 text-sm', config.text)}>{message}</p>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className={cn(
            'shrink-0 rounded-sm p-0.5 transition-colors hover:opacity-70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
            config.text
          )}
          aria-label="Dismiss alert"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
