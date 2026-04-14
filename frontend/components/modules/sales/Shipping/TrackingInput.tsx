'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { carriers } from '@/lib/validations/shipping';

interface TrackingInputProps {
  value?: string;
  onChange: (value: string) => void;
  carrier?: string;
  error?: string;
}

function getTrackingUrl(carrier: string, trackingNumber: string): string | null {
  const urls: Record<string, string> = {
    DHL: `https://www.dhl.com/en/express/tracking.html?AWB=${trackingNumber}`,
    FEDEX: `https://www.fedex.com/fedextrack/?trknbr=${trackingNumber}`,
    UPS: `https://www.ups.com/track?tracknum=${trackingNumber}`,
  };
  return urls[carrier] ?? null;
}

export function TrackingInput({ value, onChange, carrier, error }: TrackingInputProps) {
  const carrierInfo = carriers.find((c) => c.value === carrier);
  const hint = carrierInfo?.hint ?? 'Tracking number';
  const trackingUrl = carrier && value ? getTrackingUrl(carrier, value) : null;

  const handleChange = (raw: string) => {
    onChange(raw.toUpperCase().replace(/\s/g, ''));
  };

  return (
    <div className="space-y-1.5">
      <Label>Tracking Number</Label>
      <Input
        value={value ?? ''}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={hint}
        className={error ? 'border-red-500' : ''}
      />
      {trackingUrl && (
        <a
          href={trackingUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-600 hover:underline"
        >
          Track package →
        </a>
      )}
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
