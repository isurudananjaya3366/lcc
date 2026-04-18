'use client';

import { Check, X } from 'lucide-react';
import { cn } from '@/lib/cn';

interface PasswordRequirementsProps {
  password: string;
}

const requirements = [
  { label: 'At least 8 characters', test: (pw: string) => pw.length >= 8 },
  { label: 'One uppercase letter', test: (pw: string) => /[A-Z]/.test(pw) },
  { label: 'One lowercase letter', test: (pw: string) => /[a-z]/.test(pw) },
  { label: 'One number', test: (pw: string) => /[0-9]/.test(pw) },
  { label: 'One special character', test: (pw: string) => /[^A-Za-z0-9]/.test(pw) },
];

export function PasswordRequirements({ password }: PasswordRequirementsProps) {
  return (
    <ul className="space-y-1">
      {requirements.map((req) => {
        const met = password ? req.test(password) : false;
        return (
          <li key={req.label} className={cn('flex items-center gap-2 text-xs', met ? 'text-green-600' : 'text-muted-foreground')}>
            {met ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
            {req.label}
          </li>
        );
      })}
    </ul>
  );
}
