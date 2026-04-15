'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { PlanFeaturesList } from './PlanFeaturesList';
import type { SubscriptionPlan } from '@/types/settings';

interface CurrentPlanCardProps {
  plan: SubscriptionPlan;
  nextBillingDate?: string;
  onUpgrade: () => void;
  onCancel?: () => void;
}

function formatLKR(amount: number) {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
  }).format(amount);
}

export function CurrentPlanCard({
  plan,
  nextBillingDate,
  onUpgrade,
  onCancel,
}: CurrentPlanCardProps) {
  const isFree = plan.price === 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-xl">Current Plan</CardTitle>
            <p className="text-muted-foreground text-sm">Your current subscription details</p>
          </div>
          <Badge variant="secondary" className="text-sm">
            {plan.name}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold">{isFree ? 'Free' : formatLKR(plan.price)}</span>
          {!isFree && (
            <span className="text-muted-foreground text-sm">
              /{plan.interval === 'monthly' ? 'month' : 'year'}
            </span>
          )}
        </div>

        {nextBillingDate && (
          <p className="text-sm text-muted-foreground">
            Next billing date:{' '}
            <span className="font-medium text-foreground">{nextBillingDate}</span>
          </p>
        )}

        <div className="border-t pt-4">
          <p className="mb-2 text-sm font-medium">Plan features</p>
          <PlanFeaturesList features={plan.features} />
        </div>

        <div className="text-sm text-muted-foreground">
          <span>Up to {plan.maxUsers} users</span>
          <span className="mx-2">·</span>
          <span>
            {plan.maxProducts === -1
              ? 'Unlimited products'
              : `Up to ${plan.maxProducts.toLocaleString()} products`}
          </span>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button onClick={onUpgrade}>{isFree ? 'Upgrade Plan' : 'Change Plan'}</Button>
        {!isFree && onCancel && (
          <Button variant="outline" onClick={onCancel}>
            Cancel Subscription
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
