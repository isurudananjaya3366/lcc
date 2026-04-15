'use client';

import { CreditCard, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { PaymentMethod } from '@/types/settings';

interface PaymentMethodSectionProps {
  paymentMethods: PaymentMethod[];
  onAddClick: () => void;
  onSetDefault: (id: string) => void;
  onRemove: (id: string) => void;
}

function getBrandIcon(brand?: string) {
  const label = brand?.toLowerCase() ?? 'card';
  return (
    <div className="flex h-8 w-12 items-center justify-center rounded border bg-muted text-xs font-semibold uppercase">
      {label === 'visa'
        ? 'VISA'
        : label === 'mastercard'
          ? 'MC'
          : label === 'amex'
            ? 'AMEX'
            : 'CARD'}
    </div>
  );
}

export function PaymentMethodSection({
  paymentMethods,
  onAddClick,
  onSetDefault,
  onRemove,
}: PaymentMethodSectionProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Payment Methods</CardTitle>
          <Button size="sm" onClick={onAddClick}>
            <CreditCard className="mr-2 h-4 w-4" />
            Add Payment Method
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {paymentMethods.length === 0 ? (
          <p className="text-sm text-muted-foreground py-4 text-center">
            No payment methods on file. Add one to enable billing.
          </p>
        ) : (
          <div className="space-y-3">
            {paymentMethods.map((method) => (
              <div
                key={method.id}
                className="flex items-center justify-between rounded-lg border p-4"
              >
                <div className="flex items-center gap-4">
                  {getBrandIcon(method.brand)}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">•••• {method.last4}</span>
                      {method.isDefault && (
                        <Badge variant="secondary" className="text-xs">
                          Default
                        </Badge>
                      )}
                    </div>
                    {method.expiryMonth && method.expiryYear && (
                      <p className="text-sm text-muted-foreground">
                        Expires {String(method.expiryMonth).padStart(2, '0')}/{method.expiryYear}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {!method.isDefault && (
                    <Button variant="ghost" size="sm" onClick={() => onSetDefault(method.id)}>
                      Set Default
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-destructive hover:text-destructive"
                    onClick={() => onRemove(method.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
