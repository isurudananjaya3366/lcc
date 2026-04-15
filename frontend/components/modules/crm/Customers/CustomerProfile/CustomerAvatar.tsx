'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface CustomerAvatarProps {
  customer: {
    name: string;
    imageUrl?: string;
  };
  size?: 'small' | 'medium' | 'large';
  editable?: boolean;
}

const sizeClasses = {
  small: 'h-8 w-8 text-xs',
  medium: 'h-12 w-12 text-sm',
  large: 'h-24 w-24 text-2xl',
};

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  const first = parts[0] ?? '';
  const last = parts[parts.length - 1] ?? '';
  if (parts.length === 1) return first.charAt(0).toUpperCase();
  return (first.charAt(0) + last.charAt(0)).toUpperCase();
}

function getColorByInitial(initial: string): string {
  const char = initial.charAt(0).toUpperCase();
  if (char >= 'A' && char <= 'D') return 'bg-blue-500';
  if (char >= 'E' && char <= 'H') return 'bg-green-500';
  if (char >= 'I' && char <= 'L') return 'bg-purple-500';
  if (char >= 'M' && char <= 'P') return 'bg-orange-500';
  if (char >= 'Q' && char <= 'T') return 'bg-pink-500';
  return 'bg-teal-500';
}

export function CustomerAvatar({
  customer,
  size = 'large',
  editable = false,
}: CustomerAvatarProps) {
  const initials = getInitials(customer.name);
  const bgColor = getColorByInitial(initials);

  return (
    <div className="relative group">
      <Avatar className={cn(sizeClasses[size])}>
        {customer.imageUrl && <AvatarImage src={customer.imageUrl} alt={customer.name} />}
        <AvatarFallback className={cn(bgColor, 'text-white font-semibold')}>
          {initials}
        </AvatarFallback>
      </Avatar>
      {editable && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
          <span className="text-white text-xs">Edit</span>
        </div>
      )}
    </div>
  );
}
