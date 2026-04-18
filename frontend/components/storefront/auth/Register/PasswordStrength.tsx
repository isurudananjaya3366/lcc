'use client';

import { cn } from '@/lib/cn';

interface PasswordStrengthProps {
  password: string;
}

function calculateStrength(password: string): number {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  // Map 0-5 checks to 0-4 score
  if (strength <= 1) return strength;
  if (strength === 2) return 1;
  if (strength === 3) return 2;
  if (strength === 4) return 3;
  return 4;
}

const strengthConfig: Record<number, { label: string; color: string }> = {
  0: { label: '', color: 'bg-muted' },
  1: { label: 'Weak', color: 'bg-red-500' },
  2: { label: 'Fair', color: 'bg-orange-500' },
  3: { label: 'Good', color: 'bg-yellow-500' },
  4: { label: 'Strong', color: 'bg-green-500' },
};

export function PasswordStrength({ password }: PasswordStrengthProps) {
  const strength = password ? calculateStrength(password) : 0;
  const config = strengthConfig[strength] ?? { label: '', color: 'bg-muted' };
  const { label, color } = config;

  return (
    <div className="space-y-1">
      <div className="flex gap-1">
        {[1, 2, 3, 4].map((segment) => (
          <div
            key={segment}
            className={cn(
              'h-1.5 flex-1 rounded-full transition-colors',
              strength >= segment ? color : 'bg-muted',
            )}
          />
        ))}
      </div>
      {label && (
        <p className={cn('text-xs', strength <= 1 ? 'text-red-500' : strength === 2 ? 'text-orange-500' : strength === 3 ? 'text-yellow-600' : 'text-green-500')}>
          {label}
        </p>
      )}
    </div>
  );
}
