'use client';

import { Card, CardContent } from '@/components/ui/card';
import type { StoreUser } from '@/types/storefront/auth.types';

interface WelcomeCardProps {
  user: StoreUser | null;
}

export function WelcomeCard({ user }: WelcomeCardProps) {
  const firstName = user?.firstName || 'there';
  const memberSince = user?.createdAt
    ? new Intl.DateTimeFormat('en-LK', { month: 'long', year: 'numeric' }).format(
        new Date(user.createdAt)
      )
    : null;

  return (
    <Card>
      <CardContent className="pt-6">
        <h2 className="text-2xl font-bold tracking-tight">
          Welcome back, {firstName}!
        </h2>
        <p className="text-muted-foreground mt-1">
          Here&apos;s a summary of your recent activity.
        </p>
        {memberSince && (
          <p className="text-xs text-muted-foreground mt-2">
            Member since {memberSince}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
