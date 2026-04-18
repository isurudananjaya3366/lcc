import type { Metadata } from 'next';
import { ForgotPasswordPage } from '@/components/storefront/auth/ForgotPassword';

export const metadata: Metadata = {
  title: 'Forgot Password',
  description: 'Reset your account password.',
};

export default function ForgotPasswordRoute() {
  return <ForgotPasswordPage />;
}
