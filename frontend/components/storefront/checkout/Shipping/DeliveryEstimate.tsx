'use client';

import { Truck } from 'lucide-react';

interface DeliveryEstimateProps {
  estimatedDays: string;
}

export const DeliveryEstimate = ({ estimatedDays }: DeliveryEstimateProps) => {
  return (
    <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
      <Truck className="h-3 w-3" />
      Delivery in {estimatedDays}
    </span>
  );
};
