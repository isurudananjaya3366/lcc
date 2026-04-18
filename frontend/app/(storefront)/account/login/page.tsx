import type { Metadata } from 'next';
import { Suspense } from 'react';
import { LoginPage as LoginPageComponent } from '@/components/storefront/auth/Login';

export const metadata: Metadata = {
  title: 'Sign In',
  description: 'Sign in to your account.',
};

export default function LoginPage() {
  return (
    <Suspense fallback={null}>
      <LoginPageComponent />
    </Suspense>
  );
}
