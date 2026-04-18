'use client';

import { Mail, Phone } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/cn';

interface EmailPhoneToggleProps {
  value: 'email' | 'phone';
  onChange: (method: 'email' | 'phone') => void;
}

export function EmailPhoneToggle({ value, onChange }: EmailPhoneToggleProps) {
  return (
    <div className="flex rounded-lg border p-1">
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className={cn(
          'flex-1 gap-2',
          value === 'email' && 'bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground',
        )}
        onClick={() => onChange('email')}
      >
        <Mail className="h-4 w-4" />
        Email
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className={cn(
          'flex-1 gap-2',
          value === 'phone' && 'bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground',
        )}
        onClick={() => onChange('phone')}
      >
        <Phone className="h-4 w-4" />
        Phone
      </Button>
    </div>
  );
}
