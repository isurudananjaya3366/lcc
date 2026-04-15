'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Loader2, ShieldAlert } from 'lucide-react';
import Link from 'next/link';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { AuthAlert } from '@/components/auth/AuthAlert';
import { OTPInput } from '@/components/auth/OTPInput';
import { authService } from '@/services/api/authService';

type VerifyStatus = 'idle' | 'verifying' | 'error';

function TwoFactorVerifyContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [otpValue, setOtpValue] = useState('');
  const [status, setStatus] = useState<VerifyStatus>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showBackupCode, setShowBackupCode] = useState(false);
  const [backupCodeValue, setBackupCodeValue] = useState('');
  const [sessionToken, setSessionToken] = useState<string | null>(null);

  const redirectUrl = searchParams.get('redirect') || '/dashboard';

  useEffect(() => {
    const session = searchParams.get('session');
    if (!session) {
      setStatus('error');
      setErrorMessage('Session expired. Please log in again.');
      return;
    }
    setSessionToken(session);
  }, [searchParams]);

  const handleOTPVerify = async (value?: string) => {
    const code = value || otpValue;
    if (code.length !== 6 || !sessionToken) return;

    setErrorMessage(null);
    setStatus('verifying');
    try {
      await authService.verify2FALogin({ otp: code, sessionToken });
      router.push(redirectUrl);
    } catch (err: unknown) {
      setStatus('error');
      const error = err as {
        response?: { status?: number; data?: { message?: string; error?: string } };
      };
      if (error?.response?.status === 429) {
        setErrorMessage('Too many attempts. Please try again in a few minutes.');
      } else if (error?.response?.data?.error === 'session_expired') {
        setErrorMessage('Session expired. Please log in again.');
      } else {
        setErrorMessage(error?.response?.data?.message || 'Invalid code. Please try again.');
      }
      setOtpValue('');
    }
  };

  const handleBackupVerify = async () => {
    if (!backupCodeValue.trim() || !sessionToken) return;

    setErrorMessage(null);
    setStatus('verifying');
    try {
      await authService.verify2FABackupCode({
        backupCode: backupCodeValue.trim(),
        sessionToken,
      });
      router.push(redirectUrl);
    } catch (err: unknown) {
      setStatus('error');
      const error = err as { response?: { data?: { message?: string } } };
      setErrorMessage(error?.response?.data?.message || 'Invalid backup code. Please try again.');
      setBackupCodeValue('');
    }
  };

  const noSession = !sessionToken && status === 'error';

  return (
    <AuthCard>
      <div className="flex flex-col items-center gap-2">
        <ShieldAlert className="h-10 w-10 text-blue-600" />
        <AuthHeading
          title="Two-Factor Authentication"
          subtitle={
            showBackupCode ? 'Enter a backup code' : 'Enter the code from your authenticator app'
          }
        />
      </div>

      {errorMessage && (
        <AuthAlert type="error" message={errorMessage} onClose={() => setErrorMessage(null)} />
      )}

      {noSession ? (
        <div className="flex flex-col items-center gap-4 py-4">
          <Link
            href="/login"
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
          >
            Go to Login
          </Link>
        </div>
      ) : showBackupCode ? (
        /* Backup Code Mode */
        <div className="space-y-4">
          <div className="space-y-2">
            <label htmlFor="backup-code" className="block text-sm font-medium text-gray-700">
              Backup Code
            </label>
            <input
              id="backup-code"
              type="text"
              value={backupCodeValue}
              onChange={(e) => setBackupCodeValue(e.target.value.toUpperCase())}
              placeholder="XXXX-XXXX"
              disabled={status === 'verifying'}
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-center font-mono text-sm tracking-wider outline-none transition-colors focus:border-blue-500 focus:ring-2 focus:ring-blue-200 disabled:cursor-not-allowed disabled:bg-gray-50"
              autoComplete="off"
            />
          </div>

          <button
            type="button"
            onClick={handleBackupVerify}
            disabled={!backupCodeValue.trim() || status === 'verifying'}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === 'verifying' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify Backup Code'
            )}
          </button>

          <button
            type="button"
            onClick={() => {
              setShowBackupCode(false);
              setErrorMessage(null);
              setBackupCodeValue('');
            }}
            className="w-full text-center text-sm text-blue-600 hover:text-blue-500"
          >
            Use authenticator code instead
          </button>

          <p className="text-center text-xs text-gray-400">
            Lost your backup codes?{' '}
            <Link href="/support" className="text-blue-600 underline hover:text-blue-500">
              Contact Support
            </Link>
          </p>
        </div>
      ) : (
        /* OTP Mode */
        <div className="space-y-4">
          <OTPInput
            value={otpValue}
            onChange={setOtpValue}
            onComplete={handleOTPVerify}
            disabled={status === 'verifying'}
            hasError={status === 'error'}
          />

          <button
            type="button"
            onClick={() => handleOTPVerify()}
            disabled={otpValue.length !== 6 || status === 'verifying'}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {status === 'verifying' ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Verifying...
              </>
            ) : (
              'Verify'
            )}
          </button>

          <p className="text-center text-sm text-gray-500">Can&apos;t access your authenticator?</p>
          <button
            type="button"
            onClick={() => {
              setShowBackupCode(true);
              setErrorMessage(null);
              setOtpValue('');
            }}
            className="w-full text-center text-sm text-blue-600 hover:text-blue-500"
          >
            Use backup code instead
          </button>
        </div>
      )}
    </AuthCard>
  );
}

export default function TwoFactorVerifyPage() {
  return <TwoFactorVerifyContent />;
}
