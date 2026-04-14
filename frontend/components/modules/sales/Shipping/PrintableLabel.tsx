'use client';

import { Barcode, Package } from 'lucide-react';
import type { OrderAddress } from '@/types/sales';

interface PrintableLabelProps {
  orderNumber: string;
  shippingAddress: OrderAddress;
  fromAddress?: {
    name: string;
    street: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
    phone?: string;
  };
  carrier: string;
  serviceLevel: string;
  trackingNumber?: string;
  itemCount: number;
  weight?: string;
}

/**
 * Printable shipping label component with @media print styles.
 * Designed for 4x6 inch label format.
 * Task 92: Print Label
 */
export function PrintableLabel({
  orderNumber,
  shippingAddress,
  fromAddress,
  carrier,
  serviceLevel,
  trackingNumber,
  itemCount,
  weight,
}: PrintableLabelProps) {
  return (
    <>
      {/* Print-specific styles */}
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #printable-label, #printable-label * {
            visibility: visible;
          }
          #printable-label {
            position: absolute;
            left: 0;
            top: 0;
            width: 4in;
            height: 6in;
            padding: 0.25in;
            font-size: 10pt;
            color: black !important;
            background: white !important;
          }
        }
      `}</style>

      <div
        id="printable-label"
        className="mx-auto w-full max-w-[4in] border-2 border-dashed border-gray-400 bg-white p-4 text-black"
      >
        {/* Carrier & Service header */}
        <div className="mb-3 flex items-center justify-between border-b border-gray-300 pb-2">
          <div className="text-lg font-bold uppercase">{carrier || 'N/A'}</div>
          <div className="rounded bg-gray-900 px-2 py-0.5 text-xs font-bold uppercase text-white">
            {serviceLevel}
          </div>
        </div>

        {/* From Address */}
        {fromAddress ? (
          <div className="mb-3 text-xs">
            <p className="mb-0.5 font-bold uppercase text-gray-500">From</p>
            <p className="font-medium">{fromAddress.name}</p>
            <p>{fromAddress.street}</p>
            <p>
              {fromAddress.city}, {fromAddress.state} {fromAddress.postalCode}
            </p>
            <p>{fromAddress.country}</p>
            {fromAddress.phone && <p>Tel: {fromAddress.phone}</p>}
          </div>
        ) : (
          <div className="mb-3 text-xs">
            <p className="mb-0.5 font-bold uppercase text-gray-500">From</p>
            <p className="font-medium">LankaCommerce Cloud</p>
            <p>Colombo, Sri Lanka</p>
          </div>
        )}

        {/* Divider */}
        <div className="mb-3 border-t border-gray-300" />

        {/* To Address - Large */}
        <div className="mb-4">
          <p className="mb-1 text-xs font-bold uppercase text-gray-500">Ship To</p>
          <p className="text-base font-bold">
            {shippingAddress.firstName} {shippingAddress.lastName}
          </p>
          {shippingAddress.companyName && (
            <p className="text-sm font-medium">{shippingAddress.companyName}</p>
          )}
          <p className="text-sm">{shippingAddress.street}</p>
          {shippingAddress.street2 && <p className="text-sm">{shippingAddress.street2}</p>}
          <p className="text-sm font-medium">
            {shippingAddress.city}, {shippingAddress.state} {shippingAddress.postalCode}
          </p>
          <p className="text-sm">{shippingAddress.country}</p>
          {shippingAddress.phone && (
            <p className="mt-1 text-xs text-gray-600">Tel: {shippingAddress.phone}</p>
          )}
        </div>

        {/* Tracking / Barcode area */}
        <div className="mb-3 rounded border border-gray-300 bg-gray-50 p-2 text-center">
          {trackingNumber ? (
            <>
              <Barcode className="mx-auto mb-1 h-8 w-32 text-gray-700" />
              <p className="font-mono text-sm font-bold tracking-wider">{trackingNumber}</p>
            </>
          ) : (
            <p className="py-2 text-xs text-gray-400">Tracking number pending</p>
          )}
        </div>

        {/* Order info footer */}
        <div className="flex items-center justify-between border-t border-gray-300 pt-2 text-xs">
          <div className="flex items-center gap-1">
            <Package className="h-3 w-3" />
            <span className="font-medium">Order: {orderNumber}</span>
          </div>
          <div>
            {itemCount} item(s){weight && ` • ${weight}`}
          </div>
        </div>
      </div>
    </>
  );
}
