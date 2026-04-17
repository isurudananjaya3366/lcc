import { FreeShippingNote } from './FreeShippingNote';

interface DeliveryEstimateProps {
  price: number;
  freeShippingThreshold?: number;
}

export function DeliveryEstimate({
  price,
  freeShippingThreshold = 5000,
}: DeliveryEstimateProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 space-y-2">
      <div className="flex items-center gap-2 text-sm text-gray-700">
        <svg className="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 0 0-3.213-9.193 2.056 2.056 0 0 0-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 0 0-10.026 0 1.106 1.106 0 0 0-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12" />
        </svg>
        <span>Estimated delivery: <strong>3–5 business days</strong></span>
      </div>
      {price >= freeShippingThreshold && <FreeShippingNote />}
      {price < freeShippingThreshold && (
        <p className="text-xs text-gray-500">
          Add ₨ {(freeShippingThreshold - price).toLocaleString('en-LK', { minimumFractionDigits: 2 })} more for free shipping
        </p>
      )}
    </div>
  );
}
