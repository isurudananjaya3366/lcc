'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Mail, Loader2 } from 'lucide-react';
import Link from 'next/link';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { AuthAlert } from '@/components/auth/AuthAlert';
import { authService } from '@/services/api/authService';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/lib/validations/password';

export default function ResendVerificationPage() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ForgotPasswordFormData>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
  });

  const onSubmit = async (data: ForgotPasswordFormData) => {
    setError(null);
    try {
      await authService.resendVerification({ email: data.email });
      setIsSubmitted(true);
    } catch (err: unknown) {
      const error = err as { response?: { status?: number } };
      if (error?.response?.status === 429) {
        setError('Too many requests. Please wait a few minutes before trying again.');
      } else {
        // Show success even on error to prevent email enumeration
        setIsSubmitted(true);
      }
    }
  };

  return (
    <AuthCard>
      <AuthHeading
        title="Resend Verification"
        subtitle="Enter your email to receive a new verification link"
      />

      {isSubmitted ? (
        <div className="flex flex-col items-center gap-4 py-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
            <Mail className="h-8 w-8 text-blue-600" />
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-600">
              If an account exists with that email, we&apos;ve sent a new verification link.
            </p>
            <p className="mt-2 text-xs text-gray-400">
              Check your spam folder if you don&apos;t see it.
            </p>
          </div>
          <Link
            href="/login"
            className="mt-2 inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Back to Login
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {error && <AuthAlert type="error" message={error} onClose={() => setError(null)} />}

          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              disabled={isSubmitting}
              {...register('email')}
              className={`w-full rounded-lg border px-4 py-2.5 text-sm transition-colors outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 ${
                errors.email ? 'border-red-400' : 'border-gray-300'
              } ${isSubmitting ? 'cursor-not-allowed bg-gray-50' : ''}`}
            />
            {errors.email && <p className="text-xs text-red-500">{errors.email.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Sending...
              </>
            ) : (
              'Send Verification Email'
            )}
          </button>

          <p className="text-center text-sm text-gray-500">
            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Back to Login
            </Link>
          </p>
        </form>
      )}
    </AuthCard>
  );
}
