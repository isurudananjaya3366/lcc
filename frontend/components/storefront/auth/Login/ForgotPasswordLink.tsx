import Link from 'next/link';

export function ForgotPasswordLink() {
  return (
    <Link
      href="/account/forgot-password"
      className="text-sm text-blue-600 hover:underline"
    >
      Forgot password?
    </Link>
  );
}
