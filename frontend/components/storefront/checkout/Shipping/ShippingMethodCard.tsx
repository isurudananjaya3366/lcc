'use client';

import { Package, Zap } from 'lucide-react';
import { ShippingCostDisplay } from './ShippingCostDisplay';
import { DeliveryEstimate } from './DeliveryEstimate';

export interface ShippingMethodOption {
  id: string;
  name: string;
  description: string;
  price: number;
  estimatedDays: string;
  icon: 'standard' | 'express';
}

interface ShippingMethodCardProps {
  method: ShippingMethodOption;
  selected: boolean;
  disabled?: boolean;
  onSelect: (id: string) => void;
}

const iconMap = {
  standard: Package,
  express: Zap,
};

export const ShippingMethodCard = ({
  method,
  selected,
  disabled = false,
  onSelect,
}: ShippingMethodCardProps) => {
  const Icon = iconMap[method.icon];

  return (
    <button
      type="button"
      onClick={() => onSelect(method.id)}
      disabled={disabled}
      className={`w-full flex items-center gap-4 rounded-lg border-2 p-4 text-left transition-colors ${
        selected ? 'border-blue-600 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'
      } ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
    >
      <div
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
          selected ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'
        }`}
      >
        <Icon className="h-5 w-5" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{method.name}</p>
        <p className="text-xs text-muted-foreground">{method.description}</p>
        <DeliveryEstimate estimatedDays={method.estimatedDays} />
      </div>
      <div className="shrink-0">
        <ShippingCostDisplay price={method.price} />
      </div>
      <div
        className={`h-4 w-4 shrink-0 rounded-full border-2 ${
          selected ? 'border-blue-600 bg-blue-600' : 'border-gray-300'
        }`}
      >
        {selected && (
          <div className="h-full w-full flex items-center justify-center">
            <div className="h-1.5 w-1.5 rounded-full bg-white" />
          </div>
        )}
      </div>
    </button>
  );
};
