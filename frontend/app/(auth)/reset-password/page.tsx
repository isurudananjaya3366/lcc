import type { Metadata } from 'next';
import { Suspense } from 'react';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { AuthLoading } from '@/components/auth/AuthLoading';
import { ResetPasswordForm } from '@/components/auth/ResetPasswordForm';

export const metadata: Metadata = {
  title: 'Reset Password',
  description: 'Create a new password for your LankaCommerce Cloud account.',
};

export default function ResetPasswordPage() {
  return (
    <AuthCard>
      <AuthHeading title="Reset Password" subtitle="Enter your new password below" />
      <Suspense fallback={<AuthLoading message="Loading..." />}>
        <ResetPasswordForm />
      </Suspense>
    </AuthCard>
  );
}
