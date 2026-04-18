'use client';

import { useMemo } from 'react';
import { User, Truck, CreditCard, ClipboardCheck, Check } from 'lucide-react';
import { useStoreCheckoutStore } from '@/stores/store';
import { CheckoutStep } from '@/types/storefront/checkout.types';

const STEPS = [
  { step: CheckoutStep.INFORMATION, label: 'Information', icon: User },
  { step: CheckoutStep.SHIPPING, label: 'Shipping', icon: Truck },
  { step: CheckoutStep.PAYMENT, label: 'Payment', icon: CreditCard },
  { step: CheckoutStep.REVIEW, label: 'Review', icon: ClipboardCheck },
  { step: CheckoutStep.CONFIRMATION, label: 'Confirmation', icon: Check },
];

export const StepProgress = () => {
  const currentStep = useStoreCheckoutStore((s) => s.currentStep);
  const completedSteps = useStoreCheckoutStore((s) => s.completedSteps);

  const stepStates = useMemo(
    () =>
      STEPS.map(({ step }) => ({
        isCompleted: completedSteps.includes(step),
        isCurrent: currentStep === step,
        isUpcoming: currentStep < step,
      })),
    [currentStep, completedSteps]
  );

  return (
    <nav aria-label="Checkout progress" className="w-full py-4">
      <ol className="flex items-center justify-between">
        {STEPS.map(({ step, label, icon: Icon }, index) => {
          const state = stepStates[index] ?? {
            isCompleted: false,
            isCurrent: false,
            isUpcoming: true,
          };
          const { isCompleted, isCurrent } = state;
          const isActive = isCompleted || isCurrent;

          return (
            <li
              key={step}
              className="flex items-center flex-1 last:flex-none"
              aria-current={isCurrent ? 'step' : undefined}
            >
              <div className="flex flex-col items-center">
                <div
                  className={`
                    flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors
                    ${isCompleted ? 'bg-green-600 border-green-600 text-white' : ''}
                    ${isCurrent ? 'bg-blue-600 border-blue-600 text-white' : ''}
                    ${!isActive ? 'bg-white border-gray-300 text-gray-400' : ''}
                  `}
                  aria-label={`${label}: ${isCompleted ? 'completed' : isCurrent ? 'current step' : 'upcoming'}`}
                >
                  {isCompleted ? <Check className="w-5 h-5" /> : <Icon className="w-5 h-5" />}
                </div>
                <span
                  className={`
                    mt-2 text-xs font-medium hidden sm:block
                    ${isCompleted ? 'text-green-600' : ''}
                    ${isCurrent ? 'text-blue-600' : ''}
                    ${!isActive ? 'text-gray-400' : ''}
                  `}
                >
                  {label}
                </span>
              </div>
              {index < STEPS.length - 1 && (
                <div
                  className={`
                    flex-1 h-0.5 mx-2 sm:mx-4 transition-colors
                    ${isCompleted ? 'bg-green-600' : 'bg-gray-300'}
                  `}
                  aria-hidden="true"
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
