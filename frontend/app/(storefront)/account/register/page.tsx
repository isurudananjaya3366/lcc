import type { Metadata } from 'next';
import { RegisterPage } from '@/components/storefront/auth/Register';

export const metadata: Metadata = {
  title: 'Create Account',
  description: 'Create a new customer account.',
};

export default function RegisterRoute() {
  return <RegisterPage />;
}
