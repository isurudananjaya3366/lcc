'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';

import { resetPasswordSchema, type ResetPasswordFormData } from '@/lib/validations/password';
import { authService } from '@/services/api/authService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { AuthAlert } from './AuthAlert';
import { AuthLoading } from './AuthLoading';
import { PasswordStrength } from './PasswordStrength';

export function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token') ?? '';

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isTokenValid, setIsTokenValid] = useState<boolean | null>(null);
  const [countdown, setCountdown] = useState(5);

  const form = useForm<ResetPasswordFormData>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { password: '', confirmPassword: '', token },
    mode: 'onBlur',
  });

  // Validate token on mount
  useEffect(() => {
    if (!token) {
      setIsTokenValid(false);
      return;
    }
    // We assume token is valid until the backend rejects it during submission
    setIsTokenValid(true);
  }, [token]);

  // Countdown timer after success
  useEffect(() => {
    if (!isSuccess) return;
    if (countdown <= 0) {
      router.push('/login');
      return;
    }
    const timer = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(timer);
  }, [isSuccess, countdown, router]);

  async function onSubmit(data: ResetPasswordFormData) {
    setIsLoading(true);
    setError(null);

    try {
      await authService.resetPassword({
        token: data.token,
        newPassword: data.password,
        confirmPassword: data.confirmPassword,
      });
      setIsSuccess(true);
    } catch (err: unknown) {
      const errorObj = err as {
        response?: { status?: number; data?: { message?: string; code?: string } };
      };
      const status = errorObj?.response?.status;
      const code = errorObj?.response?.data?.code;
      const message = errorObj?.response?.data?.message;

      if (status === 400 && (code === 'TOKEN_EXPIRED' || code === 'TOKEN_INVALID')) {
        setIsTokenValid(false);
      } else if (message) {
        setError(message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  const password = form.watch('password');

  // Invalid or expired token
  if (isTokenValid === false) {
    return (
      <div className="text-center">
        <AuthAlert type="warning" message="This password reset link is invalid or has expired." />
        <div className="mt-6 space-y-3">
          <Link href="/forgot-password">
            <Button className="w-full">Request a New Reset Link</Button>
          </Link>
          <Link
            href="/login"
            className="block text-sm font-medium text-blue-600 transition-colors hover:text-blue-800 dark:text-blue-400"
          >
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  // Still checking token
  if (isTokenValid === null) {
    return <AuthLoading message="Validating reset link..." />;
  }

  // Success state
  if (isSuccess) {
    return (
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
          <CheckCircle2 className="h-6 w-6 text-green-600" />
        </div>
        <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Password Reset Successful
        </h2>
        <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Your password has been updated. Redirecting to login in {countdown} seconds...
        </p>
        <Link href="/login">
          <Button variant="outline" className="w-full">
            Go to Login Now
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {error && <AuthAlert type="error" message={error} onClose={() => setError(null)} />}

        <input type="hidden" {...form.register('token')} />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>New Password</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter new password"
                    autoComplete="new-password"
                    className="pr-10"
                    disabled={isLoading}
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((p) => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </FormControl>
              <PasswordStrength password={password ?? ''} />
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="confirmPassword"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm New Password</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showConfirm ? 'text' : 'password'}
                    placeholder="Re-enter new password"
                    autoComplete="new-password"
                    className="pr-10"
                    disabled={isLoading}
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm((p) => !p)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                    aria-label={showConfirm ? 'Hide password' : 'Show password'}
                    tabIndex={-1}
                  >
                    {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" size="lg" loading={isLoading} disabled={isLoading}>
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>
    </Form>
  );
}
