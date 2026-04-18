'use client';

import { useRouter } from 'next/navigation';
import { useCallback, useMemo } from 'react';
import { useStoreCheckoutStore } from '@/stores/store';
import { CheckoutStep } from '@/types/storefront/checkout.types';

const STEP_ROUTES: Record<CheckoutStep, string> = {
  [CheckoutStep.INFORMATION]: '/checkout/information',
  [CheckoutStep.SHIPPING]: '/checkout/shipping',
  [CheckoutStep.PAYMENT]: '/checkout/payment',
  [CheckoutStep.REVIEW]: '/checkout/review',
  [CheckoutStep.CONFIRMATION]: '/checkout/confirmation',
};

export function useCheckoutNavigation() {
  const router = useRouter();
  const currentStep = useStoreCheckoutStore((s) => s.currentStep);
  const completedSteps = useStoreCheckoutStore((s) => s.completedSteps);
  const setCurrentStep = useStoreCheckoutStore((s) => s.setCurrentStep);
  const completeStep = useStoreCheckoutStore((s) => s.completeStep);

  const canGoBack = useMemo(
    () => currentStep > CheckoutStep.INFORMATION,
    [currentStep]
  );

  const canProceed = useMemo(
    () => currentStep < CheckoutStep.CONFIRMATION,
    [currentStep]
  );

  const goToStep = useCallback(
    (step: CheckoutStep) => {
      setCurrentStep(step);
      router.push(STEP_ROUTES[step]);
    },
    [setCurrentStep, router]
  );

  const goToNext = useCallback(() => {
    if (!canProceed) return;
    completeStep(currentStep);
    const nextStep = (currentStep + 1) as CheckoutStep;
    goToStep(nextStep);
  }, [canProceed, currentStep, completeStep, goToStep]);

  const goToPrevious = useCallback(() => {
    if (!canGoBack) return;
    const prevStep = (currentStep - 1) as CheckoutStep;
    goToStep(prevStep);
  }, [canGoBack, currentStep, goToStep]);

  const isStepCompleted = useCallback(
    (step: CheckoutStep) => completedSteps.includes(step),
    [completedSteps]
  );

  return {
    currentStep,
    canGoBack,
    canProceed,
    goToNext,
    goToPrevious,
    goToStep,
    isStepCompleted,
  };
}
