'use client';

import { Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PlanFeaturesListProps {
  features: string[];
  unavailableFeatures?: string[];
  compact?: boolean;
}

export function PlanFeaturesList({
  features,
  unavailableFeatures = [],
  compact = false,
}: PlanFeaturesListProps) {
  return (
    <ul className={cn('space-y-2', compact && 'space-y-1')}>
      {features.map((feature) => (
        <li key={feature} className="flex items-center gap-2">
          <Check className="h-4 w-4 shrink-0 text-green-500" />
          <span className={cn('text-sm', compact && 'text-xs')}>{feature}</span>
        </li>
      ))}
      {unavailableFeatures.map((feature) => (
        <li key={feature} className="flex items-center gap-2 text-muted-foreground">
          <X className="h-4 w-4 shrink-0 text-red-400" />
          <span className={cn('text-sm line-through', compact && 'text-xs')}>{feature}</span>
        </li>
      ))}
    </ul>
  );
}
