'use client';

import { cn } from '@/lib/cn';

export interface PasswordStrengthProps {
  password: string;
  className?: string;
}

function getStrength(password: string): number {
  let score = 0;
  if (password.length >= 8) score += 25;
  if (/[A-Z]/.test(password)) score += 20;
  if (/[a-z]/.test(password)) score += 20;
  if (/[0-9]/.test(password)) score += 20;
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) score += 15;
  return score;
}

function getLabel(score: number): string {
  if (score <= 25) return 'Weak';
  if (score <= 50) return 'Fair';
  if (score <= 75) return 'Good';
  return 'Strong';
}

function getColor(score: number): string {
  if (score <= 25) return 'bg-red-500';
  if (score <= 50) return 'bg-orange-500';
  if (score <= 75) return 'bg-yellow-500';
  return 'bg-green-500';
}

function getLabelColor(score: number): string {
  if (score <= 25) return 'text-red-600';
  if (score <= 50) return 'text-orange-600';
  if (score <= 75) return 'text-yellow-600';
  return 'text-green-600';
}

const requirements = [
  { label: 'At least 8 characters', test: (pw: string) => pw.length >= 8 },
  { label: 'One uppercase letter', test: (pw: string) => /[A-Z]/.test(pw) },
  { label: 'One lowercase letter', test: (pw: string) => /[a-z]/.test(pw) },
  { label: 'One number', test: (pw: string) => /[0-9]/.test(pw) },
  {
    label: 'One special character',
    test: (pw: string) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pw),
  },
];

export function PasswordStrength({ password, className }: PasswordStrengthProps) {
  const score = getStrength(password);

  if (!password) return null;

  return (
    <div className={cn('space-y-2', className)} aria-live="polite">
      <div className="flex items-center gap-2">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-800">
          <div
            className={cn('h-full rounded-full transition-all duration-300', getColor(score))}
            style={{ width: `${score}%` }}
          />
        </div>
        <span className={cn('text-xs font-medium', getLabelColor(score))}>{getLabel(score)}</span>
      </div>
      <ul className="space-y-1">
        {requirements.map((req) => {
          const met = req.test(password);
          return (
            <li key={req.label} className="flex items-center gap-1.5 text-xs">
              <span className={met ? 'text-green-600' : 'text-gray-400'}>{met ? '✓' : '✗'}</span>
              <span className={met ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400'}>
                {req.label}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
