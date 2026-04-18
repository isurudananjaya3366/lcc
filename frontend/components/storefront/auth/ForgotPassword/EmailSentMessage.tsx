'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Mail, ArrowLeft, RefreshCw, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmailSentMessageProps {
  email: string;
  onResend: () => Promise<void>;
}

export function EmailSentMessage({ email, onResend }: EmailSentMessageProps) {
  const [cooldown, setCooldown] = useState(60);
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  const handleResend = useCallback(async () => {
    setIsResending(true);
    try {
      await onResend();
      setCooldown(60);
    } finally {
      setIsResending(false);
    }
  }, [onResend]);

  return (
    <div className="space-y-6 text-center">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <CheckCircle className="h-8 w-8 text-green-600" />
      </div>

      <div className="space-y-2">
        <h3 className="text-lg font-semibold">Check Your Inbox</h3>
        <p className="text-sm text-muted-foreground">
          We&apos;ve sent a password reset link to{' '}
          <span className="font-medium text-foreground">{email}</span>
        </p>
      </div>

      <div className="flex items-center justify-center gap-2">
        <Mail className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">
          Didn&apos;t receive the email?
        </span>
        <Button
          variant="link"
          size="sm"
          className="h-auto p-0"
          disabled={cooldown > 0 || isResending}
          onClick={handleResend}
        >
          {isResending ? (
            <RefreshCw className="mr-1 h-3 w-3 animate-spin" />
          ) : null}
          {cooldown > 0 ? `Resend in ${cooldown}s` : 'Resend'}
        </Button>
      </div>

      <Link
        href="/account/login"
        className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Sign In
      </Link>
    </div>
  );
}
