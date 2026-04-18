'use client';

import { CreditCard, Banknote } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface PaymentInfoCardProps {
  paymentMethod: string;
}

export function PaymentInfoCard({ paymentMethod }: PaymentInfoCardProps) {
  const isCOD = paymentMethod.toLowerCase().includes('cash');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <CreditCard className="h-4 w-4" />
          Payment Method
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-3 text-sm">
          {isCOD ? (
            <Banknote className="h-5 w-5 text-muted-foreground" />
          ) : (
            <CreditCard className="h-5 w-5 text-muted-foreground" />
          )}
          <span>{paymentMethod}</span>
        </div>
      </CardContent>
    </Card>
  );
}
