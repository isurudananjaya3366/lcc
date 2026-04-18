'use client';

import { useState, useEffect, useCallback } from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, Lock, Loader2, AlertCircle } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { loginSchema, type LoginFormValues } from '@/lib/validations/loginSchema';
import { useStoreAuthStore } from '@/stores/store/auth';
import { IdentifierInput } from './IdentifierInput';
import { RememberMe } from './RememberMe';
import { ForgotPasswordLink } from './ForgotPasswordLink';
import { SocialLoginSection } from './SocialLoginSection';

const LOCKOUT_DURATION = 5 * 60; // 5 minutes in seconds
const MAX_ATTEMPTS = 5;

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useStoreAuthStore((s) => s.login);

  const [showPassword, setShowPassword] = useState(false);
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [attemptCount, setAttemptCount] = useState(0);
  const [tooManyAttempts, setTooManyAttempts] = useState(false);
  const [countdown, setCountdown] = useState(0);

  const form = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      identifier: '',
      password: '',
      rememberMe: false,
    },
  });

  // Countdown timer for lockout
  useEffect(() => {
    if (countdown <= 0) {
      if (tooManyAttempts) {
        setTooManyAttempts(false);
        setAttemptCount(0);
      }
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [countdown, tooManyAttempts]);

  const formatCountdown = useCallback((seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  }, []);

  const onSubmit = async (data: Record<string, unknown>) => {
    if (tooManyAttempts) return;

    setError(null);
    setIsPending(true);

    try {
      await login(data.identifier as string, data.password as string, data.rememberMe as boolean);
      const returnUrl = searchParams.get('returnUrl') || '/';
      router.push(returnUrl);
    } catch (err) {
      const newCount = attemptCount + 1;
      setAttemptCount(newCount);
      if (newCount >= MAX_ATTEMPTS) {
        setTooManyAttempts(true);
        setCountdown(LOCKOUT_DURATION);
      }
      setError(err instanceof Error ? err.message : 'Invalid credentials');
    } finally {
      setIsPending(false);
    }
  };

  return (
    <FormProvider {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {error && !tooManyAttempts && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {tooManyAttempts && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Too many login attempts. Please try again in{' '}
              {formatCountdown(countdown)}.
            </AlertDescription>
          </Alert>
        )}

        <IdentifierInput />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    className="pl-10 pr-10"
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    tabIndex={-1}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex items-center justify-between">
          <RememberMe />
          <ForgotPasswordLink />
        </div>

        <Button
          type="submit"
          className="w-full"
          disabled={isPending || tooManyAttempts}
        >
          {isPending ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Signing in…
            </>
          ) : (
            'Sign In'
          )}
        </Button>

        <SocialLoginSection />
      </form>
    </FormProvider>
  );
}
