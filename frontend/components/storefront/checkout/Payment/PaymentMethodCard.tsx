'use client';

import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

interface PaymentMethodCardProps {
  icon: LucideIcon;
  name: string;
  description: string;
  badge?: string;
  badgeColor?: string;
  isSelected: boolean;
  onClick: () => void;
  children?: ReactNode;
}

export const PaymentMethodCard = ({
  icon: Icon,
  name,
  description,
  badge,
  badgeColor = 'bg-blue-100 text-blue-700',
  isSelected,
  onClick,
  children,
}: PaymentMethodCardProps) => {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      className={`w-full rounded-lg border-2 p-4 text-left transition-all cursor-pointer ${
        isSelected
          ? 'border-blue-600 ring-2 ring-blue-200 bg-blue-50/50'
          : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${
            isSelected ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-500'
          }`}
        >
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="text-sm font-medium text-gray-900">{name}</p>
            {badge && (
              <span
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${badgeColor}`}
              >
                {badge}
              </span>
            )}
          </div>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
        <div
          className={`h-5 w-5 shrink-0 rounded-full border-2 flex items-center justify-center ${
            isSelected ? 'border-blue-600' : 'border-gray-300'
          }`}
        >
          {isSelected && <div className="h-2.5 w-2.5 rounded-full bg-blue-600" />}
        </div>
      </div>
      {isSelected && children && (
        <div className="mt-4 border-t border-gray-200 pt-4">{children}</div>
      )}
    </div>
  );
};
