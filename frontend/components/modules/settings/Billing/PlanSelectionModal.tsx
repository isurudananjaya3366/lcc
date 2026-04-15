'use client';

import { useState } from 'react';
import { Check, X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface PlanTier {
  id: string;
  name: string;
  monthlyPrice: number;
  annualPrice: number;
  features: Record<string, string | boolean>;
}

const PLAN_TIERS: PlanTier[] = [
  {
    id: 'starter',
    name: 'Starter',
    monthlyPrice: 0,
    annualPrice: 0,
    features: {
      Users: '1',
      Products: '100',
      'Transactions/mo': '500',
      Locations: '1',
      Support: 'Email',
      Integrations: 'Limited',
    },
  },
  {
    id: 'business',
    name: 'Business',
    monthlyPrice: 4999,
    annualPrice: 47990,
    features: {
      Users: '5',
      Products: '1,000',
      'Transactions/mo': '5,000',
      Locations: '3',
      Support: 'Email + Chat',
      Integrations: 'Standard',
    },
  },
  {
    id: 'pro',
    name: 'Pro',
    monthlyPrice: 9999,
    annualPrice: 95990,
    features: {
      Users: '10',
      Products: 'Unlimited',
      'Transactions/mo': 'Unlimited',
      Locations: '10',
      Support: 'Priority',
      Integrations: 'Full',
    },
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    monthlyPrice: -1,
    annualPrice: -1,
    features: {
      Users: 'Unlimited',
      Products: 'Unlimited',
      'Transactions/mo': 'Unlimited',
      Locations: 'Unlimited',
      Support: 'Priority+',
      Integrations: 'Custom',
    },
  },
];

const FEATURE_KEYS = [
  'Users',
  'Products',
  'Transactions/mo',
  'Locations',
  'Support',
  'Integrations',
];

function formatLKR(amount: number) {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
  }).format(amount);
}

interface PlanSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan: string;
  onSelectPlan: (planId: string) => void;
}

export function PlanSelectionModal({
  isOpen,
  onClose,
  currentPlan,
  onSelectPlan,
}: PlanSelectionModalProps) {
  const [isAnnual, setIsAnnual] = useState(false);

  const currentPlanIndex = PLAN_TIERS.findIndex(
    (p) => p.name.toLowerCase() === currentPlan.toLowerCase()
  );

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Choose a Plan</DialogTitle>
          <DialogDescription>Select the plan that best fits your business needs.</DialogDescription>
        </DialogHeader>

        <div className="flex items-center justify-center gap-3 py-4">
          <Label htmlFor="billing-toggle" className={cn(!isAnnual && 'font-semibold')}>
            Monthly
          </Label>
          <Switch id="billing-toggle" checked={isAnnual} onCheckedChange={setIsAnnual} />
          <Label htmlFor="billing-toggle" className={cn(isAnnual && 'font-semibold')}>
            Annual
          </Label>
          {isAnnual && (
            <Badge variant="secondary" className="text-green-600">
              Save 20%
            </Badge>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {PLAN_TIERS.map((tier, index) => {
            const isCurrent = tier.name.toLowerCase() === currentPlan.toLowerCase();
            const isDowngrade = index < currentPlanIndex;
            const isEnterprise = tier.monthlyPrice === -1;
            const price = isAnnual ? tier.annualPrice : tier.monthlyPrice;

            return (
              <div
                key={tier.id}
                className={cn(
                  'rounded-lg border p-4 space-y-4',
                  isCurrent && 'border-primary ring-2 ring-primary/20'
                )}
              >
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg">{tier.name}</h3>
                  <div className="flex items-baseline gap-1">
                    {isEnterprise ? (
                      <span className="text-2xl font-bold">Custom</span>
                    ) : price === 0 ? (
                      <span className="text-2xl font-bold">Free</span>
                    ) : (
                      <>
                        <span className="text-2xl font-bold">{formatLKR(price)}</span>
                        <span className="text-muted-foreground text-xs">
                          /{isAnnual ? 'year' : 'month'}
                        </span>
                      </>
                    )}
                  </div>
                  {isAnnual && !isEnterprise && price > 0 && (
                    <p className="text-xs text-green-600">
                      Save {formatLKR(tier.monthlyPrice * 12 - tier.annualPrice)}/year
                    </p>
                  )}
                </div>

                <div className="space-y-2 border-t pt-4">
                  {FEATURE_KEYS.map((key) => {
                    const value = tier.features[key];
                    return (
                      <div key={key} className="flex items-center gap-2 text-sm">
                        {typeof value === 'boolean' ? (
                          value ? (
                            <Check className="h-4 w-4 text-green-500" />
                          ) : (
                            <X className="h-4 w-4 text-red-400" />
                          )
                        ) : (
                          <Check className="h-4 w-4 text-green-500" />
                        )}
                        <span>
                          {key}: <span className="font-medium">{String(value)}</span>
                        </span>
                      </div>
                    );
                  })}
                </div>

                <div className="pt-2">
                  {isCurrent ? (
                    <Button className="w-full" disabled>
                      Current Plan
                    </Button>
                  ) : isDowngrade ? (
                    <Button className="w-full" variant="outline" disabled>
                      Downgrade
                    </Button>
                  ) : isEnterprise ? (
                    <Button
                      className="w-full"
                      variant="outline"
                      onClick={() => onSelectPlan(tier.id)}
                    >
                      Contact Sales
                    </Button>
                  ) : (
                    <Button className="w-full" onClick={() => onSelectPlan(tier.id)}>
                      Select
                    </Button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </DialogContent>
    </Dialog>
  );
}
