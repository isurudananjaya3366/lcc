'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ChevronLeft } from 'lucide-react';
import { cn } from '@/lib/cn';

interface BackButtonProps {
  href?: string;
  onClick?: () => void;
  label?: string;
  className?: string;
}

export function BackButton({ href, onClick, label = 'Back', className }: BackButtonProps) {
  const router = useRouter();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      router.back();
    }
  };

  const inner = (
    <>
      <ChevronLeft className="h-4 w-4" />
      <span>{label}</span>
    </>
  );

  const sharedClasses = cn(
    'inline-flex items-center gap-1 rounded-md px-2 py-1 text-sm text-muted-foreground transition-colors',
    'hover:bg-accent hover:text-foreground',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
    className
  );

  if (href) {
    return (
      <Link href={href} className={sharedClasses}>
        {inner}
      </Link>
    );
  }

  return (
    <button type="button" onClick={handleClick} className={sharedClasses}>
      {inner}
    </button>
  );
}
