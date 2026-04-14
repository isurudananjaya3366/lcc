'use client';

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { authService } from '@/services/api/authService';

type VerificationStatus = 'idle' | 'loading' | 'success' | 'error';

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<VerificationStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(3);

  const handleVerification = useCallback(async (token: string) => {
    setStatus('loading');
    try {
      await authService.verifyEmail({ token });
      setStatus('success');
    } catch (err: unknown) {
      setStatus('error');
      const error = err as {
        response?: { status?: number; data?: { message?: string; error?: string } };
      };
      const apiError = error?.response?.data;

      if (apiError?.error === 'token_expired') {
        setErrorMessage('This verification link has expired. Please request a new one.');
      } else if (apiError?.error === 'already_verified') {
        // Already verified is not really an error — show success-like state
        setStatus('success');
        return;
      } else if (error?.response?.status === 400) {
        setErrorMessage(
          apiError?.message || 'Invalid verification link. Please request a new one.'
        );
      } else {
        setErrorMessage('Something went wrong. Please try again later.');
      }
    }
  }, []);

  // Extract token and trigger verification
  useEffect(() => {
    const token = searchParams.get('token');
    if (!token || token.trim().length === 0) {
      setStatus('error');
      setErrorMessage('No verification token found. Please check your email link.');
      return;
    }
    if (!/^[a-zA-Z0-9_-]{20,64}$/.test(token)) {
      setStatus('error');
      setErrorMessage('Invalid token format. Please request a new verification email.');
      return;
    }
    handleVerification(token);
  }, [searchParams, handleVerification]);

  // Countdown and auto-redirect on success
  useEffect(() => {
    if (status !== 'success') return;

    const interval = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          router.push('/login');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [status, router]);

  // Set page title
  useEffect(() => {
    document.title = 'Verify Email — LankaCommerce Cloud';
  }, []);

  return (
    <AuthCard>
      {status === 'loading' && (
        <>
          <AuthHeading title="Verifying Your Email" />
          <div className="flex flex-col items-center gap-4 py-8">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600" />
            <p className="text-sm text-gray-500">
              Please wait while we verify your email address...
            </p>
          </div>
        </>
      )}

      {status === 'success' && (
        <>
          <AuthHeading title="Email Verified!" />
          <div className="flex flex-col items-center gap-4 py-8">
            <CheckCircle className="h-16 w-16 text-green-500" />
            <p className="text-center text-sm text-gray-600">
              Your email has been verified successfully!
            </p>
            <p className="text-sm text-gray-400">
              Redirecting to login in {countdown} second{countdown !== 1 ? 's' : ''}...
            </p>
            <Link
              href="/login"
              className="mt-2 inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
            >
              Go to Login Now
            </Link>
          </div>
        </>
      )}

      {status === 'error' && (
        <>
          <AuthHeading title="Verification Failed" />
          <div className="flex flex-col items-center gap-4 py-8">
            <XCircle className="h-16 w-16 text-red-500" />
            <p className="text-center text-sm text-gray-600">{errorMessage}</p>
            <div className="flex flex-col items-center gap-2">
              <Link
                href="/resend-verification"
                className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
              >
                Resend Verification Email
              </Link>
              <Link href="/login" className="text-sm text-gray-500 underline hover:text-gray-700">
                Back to Login
              </Link>
            </div>
          </div>
        </>
      )}

      {status === 'idle' && (
        <>
          <AuthHeading title="Email Verification" />
          <div className="flex flex-col items-center gap-4 py-8">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        </>
      )}
    </AuthCard>
  );
}

export default function VerifyEmailPage() {
  return <VerifyEmailContent />;
}
