'use client';

import { AlertTriangle, CheckCircle } from 'lucide-react';

const COD_MAX_ORDER = 25000;
const COD_MIN_ORDER = 500;

interface CODConditionsProps {
  orderTotal?: number;
}

export const CODConditions = ({ orderTotal }: CODConditionsProps) => {
  const conditions = [
    {
      label: `Maximum order: ₨${COD_MAX_ORDER.toLocaleString()}`,
      met: orderTotal === undefined || orderTotal <= COD_MAX_ORDER,
    },
    {
      label: `Minimum order: ₨${COD_MIN_ORDER.toLocaleString()}`,
      met: orderTotal === undefined || orderTotal >= COD_MIN_ORDER,
    },
    {
      label: 'Available within Sri Lanka only',
      met: true,
    },
  ];

  const hasUnmet = conditions.some((c) => !c.met);

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-gray-600">COD Availability</p>
      <ul className="space-y-1">
        {conditions.map((condition) => (
          <li key={condition.label} className="flex items-center gap-2 text-xs">
            {condition.met ? (
              <CheckCircle className="h-3.5 w-3.5 text-green-500 shrink-0" />
            ) : (
              <AlertTriangle className="h-3.5 w-3.5 text-amber-500 shrink-0" />
            )}
            <span className={condition.met ? 'text-gray-600' : 'text-amber-700 font-medium'}>
              {condition.label}
            </span>
          </li>
        ))}
      </ul>
      {hasUnmet && (
        <div className="rounded bg-amber-50 border border-amber-200 p-2">
          <p className="text-xs text-amber-800">
            COD is not available for this order. Please select another payment method.
          </p>
        </div>
      )}
    </div>
  );
};
