'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function ResetSuccessMessage() {
  const router = useRouter();
  const [countdown, setCountdown] = useState(3);

  useEffect(() => {
    if (countdown <= 0) {
      router.push('/account/login');
      return;
    }
    const timer = setInterval(() => {
      setCountdown((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [countdown, router]);

  return (
    <div className="space-y-6 text-center">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <CheckCircle className="h-8 w-8 text-green-600" />
      </div>

      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Password Reset Successfully</h3>
        <p className="text-sm text-muted-foreground">
          You can now sign in with your new password.
        </p>
      </div>

      <p className="text-xs text-muted-foreground">
        Redirecting to sign in in {countdown}s&hellip;
      </p>

      <Button asChild className="w-full">
        <Link href="/account/login">Sign In Now</Link>
      </Button>
    </div>
  );
}
