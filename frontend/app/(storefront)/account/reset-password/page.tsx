import type { Metadata } from 'next';
import { Suspense } from 'react';
import { ResetPasswordPage } from '@/components/storefront/auth/ResetPassword';

export const metadata: Metadata = {
  title: 'Reset Password',
  description: 'Set a new password for your account.',
};

export default function ResetPasswordRoute() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center py-12 text-sm text-muted-foreground">
          Loading…
        </div>
      }
    >
      <ResetPasswordPage />
    </Suspense>
  );
}
