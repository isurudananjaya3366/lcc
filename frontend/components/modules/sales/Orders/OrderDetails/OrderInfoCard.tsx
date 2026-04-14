'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Edit, Mail, Phone, MapPin, Copy, CheckCircle } from 'lucide-react';
import type { Order, OrderAddress } from '@/types/sales';

interface OrderInfoCardProps {
  order: Order;
  onEdit?: () => void;
  isLoading?: boolean;
}

function formatAddress(address: OrderAddress): string {
  const parts = [
    address.street,
    address.street2,
    address.city,
    `${address.state}, ${address.postalCode}`,
    address.country,
  ].filter(Boolean);
  return parts.join('\n');
}

function AddressSection({
  title,
  address,
  isSameAsShipping,
}: {
  title: string;
  address?: OrderAddress;
  isSameAsShipping?: boolean;
}) {
  const handleCopy = () => {
    if (address) {
      navigator.clipboard.writeText(formatAddress(address));
    }
  };

  if (isSameAsShipping) {
    return (
      <div>
        <h4 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h4>
        <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
          <CheckCircle className="h-4 w-4" />
          <span>Same as shipping address</span>
        </div>
      </div>
    );
  }

  if (!address) {
    return (
      <div>
        <h4 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h4>
        <p className="text-sm text-gray-400">No {title.toLowerCase()} provided</p>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300">{title}</h4>
        <button
          onClick={handleCopy}
          className="rounded p-1 hover:bg-gray-100 dark:hover:bg-gray-800"
          title="Copy address"
        >
          <Copy className="h-3.5 w-3.5 text-gray-400" />
        </button>
      </div>
      <div className="space-y-0.5 text-sm text-gray-600 dark:text-gray-400">
        <p>
          {address.firstName} {address.lastName}
        </p>
        {address.companyName && <p>{address.companyName}</p>}
        <p>{address.street}</p>
        {address.street2 && <p>{address.street2}</p>}
        <p>
          {address.city}, {address.state} {address.postalCode}
        </p>
        <p>{address.country}</p>
      </div>
    </div>
  );
}

export function OrderInfoCard({ order, onEdit, isLoading }: OrderInfoCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-4 pt-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-20 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          ))}
        </CardContent>
      </Card>
    );
  }

  const isSameAddress =
    order.billingAddress &&
    order.shippingAddress &&
    order.billingAddress.street === order.shippingAddress.street &&
    order.billingAddress.city === order.shippingAddress.city &&
    order.billingAddress.postalCode === order.shippingAddress.postalCode;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-base">Order Information</CardTitle>
        {onEdit && (
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={onEdit}>
            <Edit className="h-4 w-4" />
          </Button>
        )}
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3 md:divide-x">
          {/* Customer Info */}
          <div>
            <h4 className="mb-2 text-sm font-semibold text-gray-700 dark:text-gray-300">
              Customer
            </h4>
            <div className="space-y-1.5 text-sm">
              <p className="font-medium text-gray-900 dark:text-gray-100">
                {order.customerName || 'Walk-in Customer'}
              </p>
              {order.customerId && <p className="text-xs text-gray-400">ID: {order.customerId}</p>}
              {order.customerEmail && (
                <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                  <Mail className="h-3.5 w-3.5" />
                  <a href={`mailto:${order.customerEmail}`} className="hover:underline truncate">
                    {order.customerEmail}
                  </a>
                </div>
              )}
              {order.customerPhone && (
                <div className="flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
                  <Phone className="h-3.5 w-3.5" />
                  <a href={`tel:${order.customerPhone}`} className="hover:underline">
                    {order.customerPhone}
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Shipping Address */}
          <div className="md:pl-6">
            <AddressSection title="Shipping Address" address={order.shippingAddress} />
          </div>

          {/* Billing Address */}
          <div className="md:pl-6">
            <AddressSection
              title="Billing Address"
              address={order.billingAddress}
              isSameAsShipping={isSameAddress ?? false}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
