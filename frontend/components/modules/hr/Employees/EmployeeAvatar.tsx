'use client';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

interface EmployeeAvatarProps {
  firstName: string;
  lastName: string;
  photo?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

function getInitials(firstName: string, lastName: string): string {
  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
}

function getColorFromName(name: string): string {
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-orange-500',
    'bg-pink-500',
    'bg-teal-500',
    'bg-indigo-500',
    'bg-rose-500',
  ];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length] ?? 'bg-blue-500';
}

const sizeClasses = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-10 w-10 text-sm',
  lg: 'h-16 w-16 text-lg',
};

export function EmployeeAvatar({
  firstName,
  lastName,
  photo,
  size = 'md',
  className,
}: EmployeeAvatarProps) {
  const initials = getInitials(firstName, lastName);
  const colorClass = getColorFromName(`${firstName} ${lastName}`);

  return (
    <Avatar className={cn(sizeClasses[size], className)}>
      {photo && <AvatarImage src={photo} alt={`${firstName} ${lastName}`} />}
      <AvatarFallback className={cn(colorClass, 'text-white font-medium')}>
        {initials}
      </AvatarFallback>
    </Avatar>
  );
}
