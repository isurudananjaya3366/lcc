'use client';

import Link from 'next/link';

export const LoginPrompt = () => {
  return (
    <p className="text-sm text-muted-foreground">
      Already have an account?{' '}
      <Link
        href="/auth/login?redirect=/checkout/information"
        className="font-medium text-primary underline-offset-4 hover:underline"
      >
        Log in
      </Link>
    </p>
  );
};
