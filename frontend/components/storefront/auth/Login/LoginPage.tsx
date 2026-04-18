'use client';

import Link from 'next/link';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';
import { LoginForm } from './LoginForm';
import { GuestGuard } from '../GuestGuard';

export function LoginPage() {
  return (
    <GuestGuard>
      <div className="mx-auto max-w-md space-y-6">
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Welcome Back</CardTitle>
            <CardDescription>
              Sign in to your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm />
          </CardContent>
        </Card>

        <p className="text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{' '}
          <Link href="/account/register" className="text-primary hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </GuestGuard>
  );
}
