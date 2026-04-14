import type { Metadata } from 'next';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm';

export const metadata: Metadata = {
  title: 'Forgot Password',
  description: 'Reset your LankaCommerce Cloud account password.',
};

export default function ForgotPasswordPage() {
  return (
    <AuthCard>
      <AuthHeading
        title="Forgot Password?"
        subtitle="Enter your email and we'll send you reset instructions"
      />
      <ForgotPasswordForm />
    </AuthCard>
  );
}
