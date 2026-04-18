'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckoutGuard } from '../CheckoutLayout';
import { ContactSummary } from './ContactSummary';
import { EditContactLink } from './EditContactLink';
import { ShippingSummary } from './ShippingSummary';
import { EditShippingLink } from './EditShippingLink';
import { PaymentSummary } from './PaymentSummary';
import { EditPaymentLink } from './EditPaymentLink';
import { OrderItemsReview } from './OrderItemsReview';
import { PlaceOrderButton } from './PlaceOrderButton';
import { OrderProcessing } from './OrderProcessing';

export const ReviewStep = () => {
  const [termsAccepted, setTermsAccepted] = useState(false);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  return (
    <CheckoutGuard>
      <div className="space-y-6">
        {/* Contact Information */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="text-base">Contact Information</CardTitle>
            <EditContactLink />
          </CardHeader>
          <CardContent>
            <ContactSummary />
          </CardContent>
        </Card>

        {/* Shipping */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="text-base">Shipping</CardTitle>
            <EditShippingLink />
          </CardHeader>
          <CardContent>
            <ShippingSummary />
          </CardContent>
        </Card>

        {/* Payment */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
            <CardTitle className="text-base">Payment</CardTitle>
            <EditPaymentLink />
          </CardHeader>
          <CardContent>
            <PaymentSummary />
          </CardContent>
        </Card>

        {/* Order Items */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Order Items</CardTitle>
          </CardHeader>
          <CardContent>
            <OrderItemsReview />
          </CardContent>
        </Card>

        {/* Terms */}
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={termsAccepted}
            onChange={(e) => setTermsAccepted(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-gray-300 text-green-600 focus:ring-green-500"
          />
          <span className="text-sm text-gray-600">
            I agree to the{' '}
            <a href="/terms" className="text-blue-600 underline hover:text-blue-700">
              Terms &amp; Conditions
            </a>{' '}
            and{' '}
            <a href="/privacy" className="text-blue-600 underline hover:text-blue-700">
              Privacy Policy
            </a>
            .
          </span>
        </label>

        <PlaceOrderButton disabled={!termsAccepted} />
      </div>

      <OrderProcessing />
    </CheckoutGuard>
  );
};
