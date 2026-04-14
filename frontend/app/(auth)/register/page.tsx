import type { Metadata } from 'next';
import Link from 'next/link';

import { AuthCard } from '@/components/auth/AuthCard';
import { AuthHeading } from '@/components/auth/AuthHeading';
import { RegisterForm } from '@/components/auth/RegisterForm';

export const metadata: Metadata = {
  title: 'Register',
  description: 'Create a new LankaCommerce Cloud account for your business.',
};

export default function RegisterPage() {
  return (
    <AuthCard className="max-w-lg">
      <AuthHeading title="Create Account" subtitle="Join LankaCommerce Cloud today" />
      <RegisterForm />
      <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        Already have an account?{' '}
        <Link
          href="/login"
          className="font-medium text-blue-600 transition-colors hover:text-blue-800 hover:underline dark:text-blue-400 dark:hover:text-blue-300"
        >
          Sign in
        </Link>
      </p>
    </AuthCard>
  );
}
