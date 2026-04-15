'use client';

import { Phone, Mail, MapPin, Globe, Building, Clock, CreditCard, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import type { Vendor } from '@/types/vendor';

interface OverviewTabProps {
  vendor: Vendor;
}

export function OverviewTab({ vendor }: OverviewTabProps) {
  const primaryContact = vendor.contacts?.find((c) => c.isPrimary);
  const primaryAddress = vendor.addresses?.find((a) => a.isDefault);
  const addressStr = primaryAddress
    ? [primaryAddress.street, primaryAddress.city, primaryAddress.state, primaryAddress.postalCode]
        .filter(Boolean)
        .join(', ')
    : undefined;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">Company Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { label: 'Company Name', value: vendor.companyName, icon: Building },
            {
              label: 'Contact Person',
              value: primaryContact
                ? `${primaryContact.firstName} ${primaryContact.lastName}`
                : 'N/A',
              icon: Building,
            },
            {
              label: 'Phone',
              value: vendor.phone || primaryContact?.phone,
              icon: Phone,
              href: vendor.phone ? `tel:${vendor.phone}` : undefined,
            },
            {
              label: 'Email',
              value: vendor.email || primaryContact?.email,
              icon: Mail,
              href: vendor.email ? `mailto:${vendor.email}` : undefined,
            },
            { label: 'Address', value: addressStr, icon: MapPin },
            { label: 'Website', value: vendor.website, icon: Globe, href: vendor.website },
          ].map((field, i, arr) => (
            <div key={field.label}>
              <div className="flex items-start gap-3">
                <field.icon className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
                <div className="flex-1">
                  <p className="text-xs text-muted-foreground">{field.label}</p>
                  {field.href ? (
                    <a
                      href={field.href}
                      className="text-sm text-primary hover:underline"
                      target={field.href.startsWith('http') ? '_blank' : undefined}
                      rel={field.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    >
                      {field.value || 'N/A'}
                    </a>
                  ) : (
                    <p className="text-sm">{field.value || 'N/A'}</p>
                  )}
                </div>
              </div>
              {i < arr.length - 1 && <Separator className="mt-3" />}
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">Payment Terms</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            {
              label: 'Payment Terms',
              value: vendor.paymentTerms?.replace(/_/g, ' '),
              icon: CreditCard,
            },
            { label: 'Currency', value: vendor.currency || 'LKR', icon: DollarSign },
            {
              label: 'Lead Time',
              value: vendor.averageLeadTime ? `${vendor.averageLeadTime} days` : 'N/A',
              icon: Clock,
            },
            {
              label: 'Total Purchases',
              value: `₨${vendor.totalPurchases.toLocaleString('en-LK')}`,
              icon: DollarSign,
            },
          ].map((field, i, arr) => (
            <div key={field.label}>
              <div className="flex items-start gap-3">
                <field.icon className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
                <div>
                  <p className="text-xs text-muted-foreground">{field.label}</p>
                  <p className="text-sm">{field.value || 'N/A'}</p>
                </div>
              </div>
              {i < arr.length - 1 && <Separator className="mt-3" />}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
