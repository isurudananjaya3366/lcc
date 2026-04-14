import type { Metadata } from 'next';
import Link from 'next/link';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { LoginForm } from '@/components/auth/LoginForm';

export const metadata: Metadata = {
  title: 'Login',
  description: 'Sign in to your LankaCommerce Cloud account to access the ERP dashboard.',
};

export default function LoginPage() {
  return (
    <AuthCard>
      <AuthHeading
        title="Welcome Back"
        subtitle="Sign in to your account"
      />
      <LoginForm />
      <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        Don&apos;t have an account?{' '}
        <Link
          href="/register"
          className="font-medium text-blue-600 transition-colors hover:text-blue-800 hover:underline dark:text-blue-400 dark:hover:text-blue-300"
        >
          Create account
        </Link>
      </p>
    </AuthCard>
  );
}
