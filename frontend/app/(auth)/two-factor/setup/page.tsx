'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Copy, Check, ShieldCheck } from 'lucide-react';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { AuthAlert } from '@/components/auth/AuthAlert';
import { OTPInput } from '@/components/auth/OTPInput';
import { BackupCodesDisplay } from '@/components/auth/BackupCodesDisplay';
import { authService } from '@/services/api/authService';

type SetupStatus = 'loading' | 'idle' | 'verifying' | 'success';

export default function TwoFactorSetupPage() {
  const router = useRouter();
  const [secret, setSecret] = useState<string | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [otpValue, setOtpValue] = useState('');
  const [setupStatus, setSetupStatus] = useState<SetupStatus>('loading');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [secretCopied, setSecretCopied] = useState(false);

  // Initialize 2FA setup
  useEffect(() => {
    let cancelled = false;
    async function init() {
      try {
        const data = await authService.setup2FA();
        if (cancelled) return;
        setSecret(data.secret);
        setQrCodeUrl(data.qrCodeUrl);
        setSetupStatus('idle');
      } catch {
        if (cancelled) return;
        setError('Failed to initialize 2FA setup. Please try again.');
        setSetupStatus('idle');
      }
    }
    init();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleVerify = useCallback(async () => {
    if (otpValue.length !== 6) return;
    setError(null);
    setSetupStatus('verifying');
    try {
      const result = await authService.verify2FASetup({ otp: otpValue });
      setBackupCodes(result.backupCodes);
      setSetupStatus('success');
    } catch (err: unknown) {
      setSetupStatus('idle');
      const error = err as { response?: { data?: { message?: string } } };
      setError(error?.response?.data?.message || 'Invalid code. Please try again.');
      setOtpValue('');
    }
  }, [otpValue]);

  const handleCopySecret = async () => {
    if (!secret) return;
    try {
      await navigator.clipboard.writeText(secret);
      setSecretCopied(true);
      setTimeout(() => setSecretCopied(false), 2000);
    } catch {
      // Ignore clipboard errors
    }
  };

  const formatSecret = (s: string) => s.match(/.{1,4}/g)?.join(' ') || s;

  if (setupStatus === 'loading') {
    return (
      <AuthCard>
        <AuthHeading title="Setting Up 2FA" />
        <div className="flex flex-col items-center gap-4 py-8">
          <Loader2 className="h-10 w-10 animate-spin text-blue-600" />
          <p className="text-sm text-gray-500">Generating your secret key...</p>
        </div>
      </AuthCard>
    );
  }

  if (setupStatus === 'success') {
    return (
      <AuthCard className="max-w-lg">
        <div className="flex flex-col items-center gap-2">
          <ShieldCheck className="h-12 w-12 text-green-500" />
          <AuthHeading
            title="2FA Enabled!"
            subtitle="Two-factor authentication is now active on your account"
          />
        </div>
        <BackupCodesDisplay codes={backupCodes} />
        <button
          type="button"
          onClick={() => router.push('/dashboard')}
          className="mt-4 w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          Continue to Dashboard
        </button>
      </AuthCard>
    );
  }

  return (
    <AuthCard className="max-w-lg">
      <AuthHeading
        title="Enable Two-Factor Authentication"
        subtitle="Add an extra layer of security to your account"
      />

      {error && (
        <AuthAlert type="error" onClose={() => setError(null)}>
          {error}
        </AuthAlert>
      )}

      <div className="space-y-6">
        {/* Step 1: QR Code */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Step 1: Scan QR Code</h3>
          <div className="flex justify-center rounded-lg border bg-white p-4">
            {qrCodeUrl ? (
              <img
                src={qrCodeUrl}
                alt="2FA QR Code"
                className="h-48 w-48"
                width={192}
                height={192}
              />
            ) : (
              <div className="flex h-48 w-48 items-center justify-center bg-gray-100">
                <p className="text-xs text-gray-400">QR Code unavailable</p>
              </div>
            )}
          </div>
        </div>

        {/* Step 2: Manual Key */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Step 2: Or Enter Manually</h3>
          {secret && (
            <div className="flex items-center gap-2 rounded-lg border bg-gray-50 px-4 py-3">
              <code className="flex-1 text-sm font-mono tracking-wider text-gray-800">
                {formatSecret(secret)}
              </code>
              <button
                type="button"
                onClick={handleCopySecret}
                className="shrink-0 rounded p-1.5 text-gray-500 transition-colors hover:bg-gray-200"
                aria-label="Copy secret key"
              >
                {secretCopied ? (
                  <Check className="h-4 w-4 text-green-600" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </button>
            </div>
          )}
        </div>

        {/* Step 3: Verify */}
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Step 3: Verify Code</h3>
          <OTPInput
            value={otpValue}
            onChange={setOtpValue}
            onComplete={() => handleVerify()}
            disabled={setupStatus === 'verifying'}
          />
        </div>

        <button
          type="button"
          onClick={handleVerify}
          disabled={otpValue.length !== 6 || setupStatus === 'verifying'}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {setupStatus === 'verifying' ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Verifying...
            </>
          ) : (
            'Verify and Enable 2FA'
          )}
        </button>

        {/* Compatible Apps */}
        <div className="rounded-lg border bg-gray-50 px-4 py-3">
          <p className="mb-2 text-xs font-medium text-gray-600">Compatible Apps:</p>
          <ul className="space-y-1 text-xs text-gray-500">
            <li>• Google Authenticator</li>
            <li>• Microsoft Authenticator</li>
            <li>• Authy</li>
            <li>• 1Password</li>
          </ul>
        </div>
      </div>
    </AuthCard>
  );
}
