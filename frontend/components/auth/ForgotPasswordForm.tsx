'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { ArrowLeft, Mail } from 'lucide-react';

import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/lib/validations/password';
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

export function ForgotPasswordForm() {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submittedEmail, setSubmittedEmail] = useState('');

  const form = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
    mode: 'onBlur',
  });

  async function onSubmit(data: ForgotPasswordFormData) {
    setIsLoading(true);
    setError(null);
    const email = data.email.trim().toLowerCase();

    try {
      await authService.forgotPassword({ email });
      setSubmittedEmail(email);
      setIsSubmitted(true);
    } catch (err: unknown) {
      const errorObj = err as { response?: { status?: number; data?: { message?: string } } };
      const status = errorObj?.response?.status;

      if (status === 429) {
        setError('Too many requests. Please wait a few minutes before trying again.');
      } else {
        // Always show success to prevent email enumeration
        setSubmittedEmail(email);
        setIsSubmitted(true);
      }
    } finally {
      setIsLoading(false);
    }
  }

  if (isSubmitted) {
    return (
      <div className="text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
          <Mail className="h-6 w-6 text-blue-600" />
        </div>
        <h2 className="mb-2 text-lg font-semibold text-gray-900 dark:text-gray-100">
          Check your email
        </h2>
        <p className="mb-6 text-sm text-gray-600 dark:text-gray-400">
          If an account exists for{' '}
          <span className="font-medium text-gray-900 dark:text-gray-100">{submittedEmail}</span>,
          we&apos;ve sent password reset instructions.
        </p>
        <div className="space-y-3">
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={() => {
              setIsSubmitted(false);
              form.reset();
            }}
          >
            Try a different email
          </Button>
          <Link
            href="/login"
            className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 transition-colors hover:text-blue-800 dark:text-blue-400"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4" noValidate>
        {error && <AuthAlert type="error" message={error} onClose={() => setError(null)} />}

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="name@company.com"
                  autoComplete="email"
                  inputMode="email"
                  disabled={isLoading}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" className="w-full" size="lg" loading={isLoading} disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send Reset Link'}
        </Button>

        <div className="text-center">
          <Link
            href="/login"
            className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 transition-colors hover:text-blue-800 dark:text-blue-400"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to login
          </Link>
        </div>
      </form>
    </Form>
  );
}
