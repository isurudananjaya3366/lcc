'use client';

import { AlertCircle, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrackingStep } from './TrackingStep';
import type { OrderStatus } from '@/types/storefront/portal.types';

interface OrderTrackingProps {
  status: OrderStatus;
  updatedAt?: string;
}

const STEPS = ['Placed', 'Confirmed', 'Shipped', 'Out for Delivery', 'Delivered'] as const;

const STATUS_TO_STEP: Record<OrderStatus, number> = {
  pending: 0,
  confirmed: 1,
  processing: 1,
  shipped: 2,
  out_for_delivery: 3,
  delivered: 4,
  cancelled: -1,
  returned: -1,
};

export function OrderTracking({ status, updatedAt }: OrderTrackingProps) {
  const currentStepIndex = STATUS_TO_STEP[status];
  const isCancelled = status === 'cancelled';
  const isReturned = status === 'returned';

  if (isCancelled || isReturned) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Order Tracking</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3 rounded-lg border border-dashed p-4">
            {isCancelled ? (
              <AlertCircle className="h-6 w-6 text-red-500" />
            ) : (
              <RotateCcw className="h-6 w-6 text-gray-500" />
            )}
            <div>
              <p className="font-medium">
                {isCancelled ? 'Order Cancelled' : 'Order Returned'}
              </p>
              {updatedAt && (
                <p className="text-sm text-muted-foreground">
                  {new Date(updatedAt).toLocaleDateString('en-LK', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Order Tracking</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-start">
          {STEPS.map((label, index) => (
            <TrackingStep
              key={label}
              label={label}
              isCompleted={index < currentStepIndex}
              isCurrent={index === currentStepIndex}
              isFirst={index === 0}
              isLast={index === STEPS.length - 1}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
