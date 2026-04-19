'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { ShippingRate } from '@/types/storefront/cms.types';
import { getShippingRates } from '@/services/storefront/cmsService';
import { PageLayout, PageHeader } from '@/components/storefront/cms/Layout';
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from '@/components/ui/table';

export function ShippingPage() {
  const [rates, setRates] = useState<ShippingRate[]>([]);

  useEffect(() => {
    getShippingRates().then(setRates);
  }, []);

  return (
    <PageLayout className="max-w-4xl">
      <PageHeader
        title="Shipping Information"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'Shipping Information' },
        ]}
      />

      <p className="text-sm text-muted-foreground -mt-4 mb-8">
        Last updated: January 1, 2026
      </p>

      <div className="space-y-10">
        {/* Delivery Areas */}
        <section className="space-y-3">
          <h2 className="text-xl font-semibold tracking-tight">Delivery Areas</h2>
          <p className="text-muted-foreground">
            We currently deliver across all provinces of Sri Lanka. Delivery times and
            rates vary depending on your location. Colombo and Western Province enjoy
            the fastest delivery times.
          </p>
        </section>

        {/* Shipping Rates Table */}
        <section className="space-y-3">
          <h2 className="text-xl font-semibold tracking-tight">Shipping Rates</h2>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Zone</TableHead>
                  <TableHead>Method</TableHead>
                  <TableHead>Estimated Delivery</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rates.map((rate) => (
                  <TableRow key={rate.id}>
                    <TableCell className="font-medium">{rate.zone}</TableCell>
                    <TableCell>{rate.method}</TableCell>
                    <TableCell>
                      {rate.minDays === 0
                        ? `Same day – ${rate.maxDays} day${rate.maxDays !== 1 ? 's' : ''}`
                        : `${rate.minDays}–${rate.maxDays} business days`}
                    </TableCell>
                    <TableCell className="text-right">
                      <span>₨{rate.price.toLocaleString()}</span>
                      {rate.freeAbove && (
                        <span className="block text-xs text-green-600">
                          Free above ₨{rate.freeAbove.toLocaleString()}
                        </span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </section>

        {/* Processing Time */}
        <section className="space-y-3">
          <h2 className="text-xl font-semibold tracking-tight">Processing Time</h2>
          <p className="text-muted-foreground">
            Orders are processed within 24 hours of placement on business days. Orders
            placed on weekends or public holidays will be processed on the next business
            day. You will receive a confirmation email once your order is dispatched.
          </p>
        </section>

        {/* Tracking */}
        <section className="space-y-3">
          <h2 className="text-xl font-semibold tracking-tight">Tracking</h2>
          <p className="text-muted-foreground">
            A tracking number is provided via email and SMS once your order is shipped.
            You can track your delivery status through our website or the courier
            partner&apos;s tracking page.
          </p>
        </section>

        {/* Related */}
        <div className="border-t pt-8">
          <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
            Related Policies
          </h3>
          <ul className="flex flex-wrap gap-3">
            <li>
              <Link href="/returns" className="text-sm text-primary hover:underline">
                Return Policy
              </Link>
            </li>
            <li>
              <Link href="/terms" className="text-sm text-primary hover:underline">
                Terms &amp; Conditions
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </PageLayout>
  );
}
