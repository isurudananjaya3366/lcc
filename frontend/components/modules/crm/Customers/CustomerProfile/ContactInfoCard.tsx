'use client';

import { Phone, Mail, MapPin, Building } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

interface ContactInfoCardProps {
  customer: {
    phone?: string;
    email?: string;
    address?: string;
    type: string;
  };
  editable?: boolean;
  onEdit?: () => void;
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
}

export function ContactInfoCard({ customer, editable, onEdit }: ContactInfoCardProps) {
  const fields = [
    {
      label: 'Phone',
      value: customer.phone,
      icon: Phone,
      action: customer.phone ? () => copyToClipboard(customer.phone!) : undefined,
      href: customer.phone ? `tel:${customer.phone}` : undefined,
    },
    {
      label: 'Email',
      value: customer.email,
      icon: Mail,
      action: customer.email ? () => copyToClipboard(customer.email!) : undefined,
      href: customer.email ? `mailto:${customer.email}` : undefined,
    },
    {
      label: 'Address',
      value: customer.address,
      icon: MapPin,
    },
    {
      label: 'Type',
      value: customer.type,
      icon: Building,
    },
  ];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base font-medium">Contact Information</CardTitle>
        {editable && (
          <Button variant="ghost" size="sm" onClick={onEdit}>
            Edit
          </Button>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.label}>
            <div className="flex items-start gap-3">
              <field.icon className="h-4 w-4 mt-0.5 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-muted-foreground">{field.label}</p>
                {field.href ? (
                  <a
                    href={field.href}
                    className="text-sm text-primary hover:underline cursor-pointer"
                    onClick={(e) => {
                      if (field.action) {
                        e.preventDefault();
                        field.action();
                      }
                    }}
                  >
                    {field.value || 'N/A'}
                  </a>
                ) : (
                  <p className="text-sm">{field.value || 'N/A'}</p>
                )}
              </div>
            </div>
            {index < fields.length - 1 && <Separator className="mt-3" />}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
