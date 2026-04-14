'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import {
  registrationSchema,
  businessInfoSchema,
  adminUserSchema,
  contactInfoSchema,
  planSelectionSchema,
  type RegistrationFormData,
} from '@/lib/validations/register';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { AuthAlert } from '@/components/auth/AuthAlert';
import { StepIndicator } from '@/components/auth/StepIndicator';
import { BusinessInfoStep } from './register/BusinessInfoStep';
import { AdminUserStep } from './register/AdminUserStep';
import { ContactInfoStep } from './register/ContactInfoStep';
import { PlanSelectionStep } from './register/PlanSelectionStep';
import apiClient from '@/services/api/apiClient';

const TOTAL_STEPS = 4;

const stepSchemas = [
  businessInfoSchema,
  adminUserSchema,
  contactInfoSchema,
  planSelectionSchema,
] as const;

const stepFields: (keyof RegistrationFormData)[][] = [
  ['businessName', 'businessType', 'registrationNumber'],
  ['firstName', 'lastName', 'email', 'password', 'confirmPassword'],
  ['phone', 'address', 'timezone'],
  ['plan'],
];

export interface RegisterFormProps {
  onSuccess?: () => void;
}

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<RegistrationFormData>({
    resolver: zodResolver(registrationSchema),
    defaultValues: {
      businessName: '',
      businessType: undefined,
      registrationNumber: '',
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      phone: '',
      address: { street: '', city: '', postalCode: '' },
      timezone: 'Asia/Colombo',
      plan: undefined,
      acceptTerms: false as unknown as true,
    },
    mode: 'onBlur',
  });

  async function validateCurrentStep(): Promise<boolean> {
    const fields = stepFields[currentStep - 1];
    const result = await form.trigger(fields);
    return result;
  }

  async function handleNext() {
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < TOTAL_STEPS) {
      setCurrentStep((s) => s + 1);
    }
  }

  function handlePrevious() {
    if (currentStep > 1) {
      setCurrentStep((s) => s - 1);
    }
  }

  async function onSubmit(data: RegistrationFormData) {
    setIsLoading(true);
    setError(null);

    try {
      const payload = {
        tenant: {
          businessName: data.businessName,
          businessType: data.businessType,
          registrationNumber: data.registrationNumber || undefined,
        },
        adminUser: {
          firstName: data.firstName,
          lastName: data.lastName,
          email: data.email,
          password: data.password,
        },
        contact: {
          phone: data.phone,
          address: data.address,
          timezone: data.timezone,
        },
        subscription: {
          plan: data.plan,
        },
        terms: {
          accepted: true,
          acceptedAt: new Date().toISOString(),
        },
      };

      await apiClient.post('/auth/register', payload);

      if (onSuccess) {
        onSuccess();
      } else {
        router.push(`/verify-email?email=${encodeURIComponent(data.email)}`);
      }
    } catch (err: unknown) {
      const errorObj = err as {
        response?: { status?: number; data?: { message?: string; errors?: Record<string, string[]> } };
      };
      const status = errorObj?.response?.status;
      const responseData = errorObj?.response?.data;

      if (status === 409) {
        setError('This email is already registered. Please sign in or use a different email.');
        setCurrentStep(2);
        form.setError('email', { message: 'Email already registered' });
      } else if (status === 400 && responseData?.errors) {
        const fieldErrors = responseData.errors;
        for (const [field, messages] of Object.entries(fieldErrors)) {
          form.setError(field as keyof RegistrationFormData, {
            message: Array.isArray(messages) ? messages[0] : String(messages),
          });
        }
        setError('Please fix the errors below and try again.');
      } else if (responseData?.message) {
        setError(responseData.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6" noValidate>
        <StepIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />

        {error && (
          <AuthAlert type="error" message={error} onClose={() => setError(null)} />
        )}

        {/* Step Content */}
        {currentStep === 1 && <BusinessInfoStep form={form} disabled={isLoading} />}
        {currentStep === 2 && <AdminUserStep form={form} disabled={isLoading} />}
        {currentStep === 3 && <ContactInfoStep form={form} disabled={isLoading} />}
        {currentStep === 4 && (
          <>
            <PlanSelectionStep form={form} disabled={isLoading} />
            <FormField
              control={form.control}
              name="acceptTerms"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-2 space-y-0 pt-2">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      disabled={isLoading}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel className="cursor-pointer text-sm font-normal">
                      I agree to the{' '}
                      <Link
                        href="/terms"
                        target="_blank"
                        className="text-blue-600 underline hover:text-blue-800"
                      >
                        Terms of Service
                      </Link>{' '}
                      and{' '}
                      <Link
                        href="/privacy"
                        target="_blank"
                        className="text-blue-600 underline hover:text-blue-800"
                      >
                        Privacy Policy
                      </Link>
                    </FormLabel>
                    <FormMessage />
                  </div>
                </FormItem>
              )}
            />
          </>
        )}

        {/* Navigation */}
        <div className="flex gap-3">
          {currentStep > 1 && (
            <Button
              type="button"
              variant="outline"
              onClick={handlePrevious}
              disabled={isLoading}
              className="flex-1"
            >
              Previous
            </Button>
          )}
          {currentStep < TOTAL_STEPS ? (
            <Button
              type="button"
              onClick={handleNext}
              disabled={isLoading}
              className="flex-1"
            >
              Next
            </Button>
          ) : (
            <Button
              type="submit"
              loading={isLoading}
              disabled={isLoading}
              className="flex-1"
              aria-busy={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
}
