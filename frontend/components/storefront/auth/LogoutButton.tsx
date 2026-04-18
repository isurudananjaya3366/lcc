'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { LogOut, Loader2 } from 'lucide-react';
import { clearTokens } from '@/services/storefront/tokenService';
import { logoutApi } from '@/services/storefront/authService';
import { useStoreAuthStore } from '@/stores/store';
import { cn } from '@/lib/cn';

export interface LogoutButtonProps {
  className?: string;
  variant?: 'default' | 'ghost' | 'outline' | 'destructive' | 'secondary' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  showIcon?: boolean;
  children?: React.ReactNode;
}

export function LogoutButton({
  className,
  variant = 'ghost',
  size = 'default',
  showIcon = true,
  children,
}: LogoutButtonProps) {
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const logout = useStoreAuthStore((s) => s.logout);
  const router = useRouter();

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      // Best-effort server logout
      await logoutApi().catch(() => {});
    } finally {
      clearTokens();
      logout();
      setIsLoggingOut(false);
      router.push('/');
    }
  };

  return (
    <Button
      variant={variant}
      size={size}
      className={cn(className)}
      onClick={handleLogout}
      disabled={isLoggingOut}
    >
      {isLoggingOut ? (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      ) : showIcon ? (
        <LogOut className="mr-2 h-4 w-4" />
      ) : null}
      {children ?? 'Sign Out'}
    </Button>
  );
}
