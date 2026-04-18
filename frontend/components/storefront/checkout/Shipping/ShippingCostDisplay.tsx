'use client';

interface ShippingCostDisplayProps {
  price: number;
}

export const ShippingCostDisplay = ({ price }: ShippingCostDisplayProps) => {
  if (price === 0) {
    return <span className="text-sm font-semibold text-green-600">Free</span>;
  }

  return <span className="text-sm font-semibold text-gray-900">₨ {price.toLocaleString()}</span>;
};
