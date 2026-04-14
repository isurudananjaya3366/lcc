'use client';

import type { UseFormReturn } from 'react-hook-form';
import { Check } from 'lucide-react';

import { cn } from '@/lib/cn';
import { FormControl, FormField, FormItem, FormMessage } from '@/components/ui/form';
import type { RegistrationFormData } from '@/lib/validations/register';

const PLANS = [
  {
    value: 'starter' as const,
    name: 'Starter',
    price: '₨5,000',
    period: '/month',
    features: [
      'Up to 5 users',
      'Basic POS',
      'Inventory management',
      'Basic reports',
      'Email support',
    ],
  },
  {
    value: 'professional' as const,
    name: 'Professional',
    price: '₨15,000',
    period: '/month',
    popular: true,
    features: [
      'Up to 25 users',
      'Advanced POS',
      'Multi-warehouse',
      'Advanced reports & analytics',
      'Priority support',
      'HR & Payroll',
    ],
  },
  {
    value: 'enterprise' as const,
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    features: [
      'Unlimited users',
      'Full ERP suite',
      'Multi-branch',
      'Custom integrations',
      'Dedicated support',
      'SLA guarantee',
    ],
  },
] as const;

interface PlanSelectionStepProps {
  form: UseFormReturn<RegistrationFormData>;
  disabled?: boolean;
}

export function PlanSelectionStep({ form, disabled }: PlanSelectionStepProps) {
  return (
    <FormField
      control={form.control}
      name="plan"
      render={({ field }) => (
        <FormItem>
          <FormControl>
            <div className="space-y-3">
              {PLANS.map((plan) => {
                const isSelected = field.value === plan.value;
                return (
                  <button
                    key={plan.value}
                    type="button"
                    disabled={disabled}
                    onClick={() => field.onChange(plan.value)}
                    className={cn(
                      'relative w-full rounded-lg border-2 p-4 text-left transition-colors',
                      isSelected
                        ? 'border-blue-600 bg-blue-50 dark:bg-blue-950/20'
                        : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600',
                      disabled && 'cursor-not-allowed opacity-50'
                    )}
                  >
                    {plan.popular && (
                      <span className="absolute -top-2.5 right-4 rounded-full bg-blue-600 px-2 py-0.5 text-xs font-medium text-white">
                        Popular
                      </span>
                    )}
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                          {plan.name}
                        </h3>
                        <p className="mt-1">
                          <span className="text-lg font-bold text-gray-900 dark:text-gray-100">
                            {plan.price}
                          </span>
                          {plan.period && (
                            <span className="text-sm text-gray-500">{plan.period}</span>
                          )}
                        </p>
                      </div>
                      <div
                        className={cn(
                          'flex h-5 w-5 items-center justify-center rounded-full border-2',
                          isSelected
                            ? 'border-blue-600 bg-blue-600'
                            : 'border-gray-300 dark:border-gray-600'
                        )}
                      >
                        {isSelected && <Check className="h-3 w-3 text-white" />}
                      </div>
                    </div>
                    <ul className="mt-3 space-y-1">
                      {plan.features.map((feature) => (
                        <li
                          key={feature}
                          className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
                        >
                          <Check className="h-3.5 w-3.5 text-green-500" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </button>
                );
              })}
            </div>
          </FormControl>
          <FormMessage />
        </FormItem>
      )}
    />
  );
}
