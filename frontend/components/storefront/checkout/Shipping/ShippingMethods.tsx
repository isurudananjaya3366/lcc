'use client';

import { useFormContext, useWatch } from 'react-hook-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ShippingMethodCard, type ShippingMethodOption } from './ShippingMethodCard';
import { FormFieldError } from '../Information/FormFieldError';
import type { ShippingStepData } from '@/lib/validations/checkoutSchemas';

const shippingMethods: ShippingMethodOption[] = [
  {
    id: 'standard',
    name: 'Standard Shipping',
    description: 'Delivered via Sri Lanka Post or local courier',
    price: 250,
    estimatedDays: '3-5 business days',
    icon: 'standard',
  },
  {
    id: 'express',
    name: 'Express Shipping',
    description: 'Priority delivery via express courier',
    price: 500,
    estimatedDays: '1-2 business days',
    icon: 'express',
  },
];

export const ShippingMethods = () => {
  const { setValue } = useFormContext<ShippingStepData>();
  const selectedMethodId = useWatch<ShippingStepData>({ name: 'shippingMethodId' });
  const province = useWatch<ShippingStepData>({ name: 'province' });

  const hasAddress = !!province;

  const handleSelect = (id: string) => {
    setValue('shippingMethodId', id, { shouldValidate: true });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Select a delivery method</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {!hasAddress ? (
          <p className="text-sm text-muted-foreground py-2">
            Please select an address first to see available shipping methods.
          </p>
        ) : (
          <>
            {shippingMethods.map((method) => (
              <ShippingMethodCard
                key={method.id}
                method={method}
                selected={selectedMethodId === method.id}
                onSelect={handleSelect}
              />
            ))}
          </>
        )}
        <FormFieldError fieldName="shippingMethodId" />
      </CardContent>
    </Card>
  );
};

export { shippingMethods };
