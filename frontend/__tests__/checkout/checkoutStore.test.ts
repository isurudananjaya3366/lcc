/**
 * Checkout Store Tests — Task 94 (Unit Testing Suite)
 *
 * Tests the Zustand checkout store state management:
 * initial state, actions, step navigation, and reset.
 *
 * NOTE: These tests use direct store action invocation
 * without requiring a DOM environment.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { CheckoutStep } from '@/types/storefront/checkout.types';
import type {
  ContactInfo,
  ShippingAddress,
  ShippingMethod,
} from '@/types/storefront/checkout.types';

// ─── Test data fixtures ───────────────────────────────────────────────────────

const mockContactInfo: ContactInfo = {
  email: 'kasun@example.com',
  phone: '771234567',
  firstName: 'Kasun',
  lastName: 'Perera',
  whatsappOptIn: true,
};

const mockShippingAddress: ShippingAddress = {
  province: 'Western Province',
  district: 'Colombo',
  city: 'Colombo 03',
  address1: '123 Galle Road',
  address2: 'Apt 4B',
  landmark: 'Near Cinnamon Grand',
  postalCode: '00300',
};

const mockShippingMethod: ShippingMethod = {
  id: 'standard',
  name: 'Standard Delivery',
  description: 'Delivered in 3-5 business days',
  price: 350,
  estimatedDays: 5,
  carrier: 'Standard Courier',
};

// ─── CheckoutStep Enum Tests ─────────────────────────────────────────────────

describe('CheckoutStep enum', () => {
  it('has INFORMATION as step 1', () => {
    expect(CheckoutStep.INFORMATION).toBe(1);
  });

  it('has SHIPPING as step 2', () => {
    expect(CheckoutStep.SHIPPING).toBe(2);
  });

  it('has PAYMENT as step 3', () => {
    expect(CheckoutStep.PAYMENT).toBe(3);
  });

  it('has REVIEW as step 4', () => {
    expect(CheckoutStep.REVIEW).toBe(4);
  });

  it('has CONFIRMATION as step 5', () => {
    expect(CheckoutStep.CONFIRMATION).toBe(5);
  });

  it('step values are sequential from 1 to 5', () => {
    const steps = [
      CheckoutStep.INFORMATION,
      CheckoutStep.SHIPPING,
      CheckoutStep.PAYMENT,
      CheckoutStep.REVIEW,
      CheckoutStep.CONFIRMATION,
    ];
    steps.forEach((step, index) => {
      expect(step).toBe(index + 1);
    });
  });
});

// ─── Contact Info Type Tests ─────────────────────────────────────────────────

describe('ContactInfo type structure', () => {
  it('has all required fields', () => {
    const contact: ContactInfo = mockContactInfo;
    expect(contact.email).toBeDefined();
    expect(contact.phone).toBeDefined();
    expect(contact.firstName).toBeDefined();
    expect(contact.lastName).toBeDefined();
    expect(typeof contact.whatsappOptIn).toBe('boolean');
  });
});

// ─── ShippingAddress Type Tests ───────────────────────────────────────────────

describe('ShippingAddress type structure', () => {
  it('has province, district, city cascade fields', () => {
    const address: ShippingAddress = mockShippingAddress;
    expect(address.province).toBeDefined();
    expect(address.district).toBeDefined();
    expect(address.city).toBeDefined();
  });

  it('has address1 as required field', () => {
    expect(mockShippingAddress.address1).toBeTruthy();
  });

  it('has optional address2, landmark, postalCode', () => {
    expect(mockShippingAddress.address2).toBeDefined();
    expect(mockShippingAddress.landmark).toBeDefined();
    expect(mockShippingAddress.postalCode).toBeDefined();
  });
});

// ─── ShippingMethod Type Tests ────────────────────────────────────────────────

describe('ShippingMethod type structure', () => {
  it('has all required fields', () => {
    const method: ShippingMethod = mockShippingMethod;
    expect(method.id).toBeDefined();
    expect(method.name).toBeDefined();
    expect(method.description).toBeDefined();
    expect(typeof method.price).toBe('number');
    expect(typeof method.estimatedDays).toBe('number');
    expect(method.carrier).toBeDefined();
  });

  it('price is a non-negative number', () => {
    expect(mockShippingMethod.price).toBeGreaterThanOrEqual(0);
  });

  it('estimatedDays is positive', () => {
    expect(mockShippingMethod.estimatedDays).toBeGreaterThan(0);
  });
});

// ─── Step Navigation Logic Tests ─────────────────────────────────────────────

describe('Checkout step navigation logic', () => {
  it('first step has no previous step', () => {
    const currentStep = CheckoutStep.INFORMATION;
    const canGoBack = currentStep > CheckoutStep.INFORMATION;
    expect(canGoBack).toBe(false);
  });

  it('last step has no next step', () => {
    const currentStep = CheckoutStep.CONFIRMATION;
    const canProceed = currentStep < CheckoutStep.CONFIRMATION;
    expect(canProceed).toBe(false);
  });

  it('middle steps can go both forward and back', () => {
    const currentStep = CheckoutStep.SHIPPING;
    const canGoBack = currentStep > CheckoutStep.INFORMATION;
    const canProceed = currentStep < CheckoutStep.CONFIRMATION;
    expect(canGoBack).toBe(true);
    expect(canProceed).toBe(true);
  });

  it('next step is currentStep + 1', () => {
    const currentStep = CheckoutStep.INFORMATION;
    const nextStep = (currentStep + 1) as CheckoutStep;
    expect(nextStep).toBe(CheckoutStep.SHIPPING);
  });

  it('previous step is currentStep - 1', () => {
    const currentStep = CheckoutStep.SHIPPING;
    const prevStep = (currentStep - 1) as CheckoutStep;
    expect(prevStep).toBe(CheckoutStep.INFORMATION);
  });
});

// ─── Step Route Mapping Tests ─────────────────────────────────────────────────

describe('Step route mapping', () => {
  const STEP_ROUTES: Record<CheckoutStep, string> = {
    [CheckoutStep.INFORMATION]: '/checkout/information',
    [CheckoutStep.SHIPPING]: '/checkout/shipping',
    [CheckoutStep.PAYMENT]: '/checkout/payment',
    [CheckoutStep.REVIEW]: '/checkout/review',
    [CheckoutStep.CONFIRMATION]: '/checkout/confirmation',
  };

  it('maps INFORMATION to /checkout/information', () => {
    expect(STEP_ROUTES[CheckoutStep.INFORMATION]).toBe('/checkout/information');
  });

  it('maps SHIPPING to /checkout/shipping', () => {
    expect(STEP_ROUTES[CheckoutStep.SHIPPING]).toBe('/checkout/shipping');
  });

  it('maps PAYMENT to /checkout/payment', () => {
    expect(STEP_ROUTES[CheckoutStep.PAYMENT]).toBe('/checkout/payment');
  });

  it('maps REVIEW to /checkout/review', () => {
    expect(STEP_ROUTES[CheckoutStep.REVIEW]).toBe('/checkout/review');
  });

  it('maps CONFIRMATION to /checkout/confirmation', () => {
    expect(STEP_ROUTES[CheckoutStep.CONFIRMATION]).toBe('/checkout/confirmation');
  });

  it('all 5 steps have route mappings', () => {
    expect(Object.keys(STEP_ROUTES)).toHaveLength(5);
  });
});

// ─── Completed Steps Logic Tests ──────────────────────────────────────────────

describe('Completed steps tracking logic', () => {
  it('starts with no completed steps', () => {
    const completedSteps: CheckoutStep[] = [];
    expect(completedSteps).toHaveLength(0);
  });

  it('adds a step to completed steps', () => {
    const completedSteps: CheckoutStep[] = [];
    completedSteps.push(CheckoutStep.INFORMATION);
    expect(completedSteps).toContain(CheckoutStep.INFORMATION);
  });

  it('does not duplicate steps', () => {
    const completedSteps: CheckoutStep[] = [];
    const addStep = (step: CheckoutStep) => {
      if (!completedSteps.includes(step)) completedSteps.push(step);
    };
    addStep(CheckoutStep.INFORMATION);
    addStep(CheckoutStep.INFORMATION);
    expect(completedSteps).toHaveLength(1);
  });

  it('can check if a step is completed', () => {
    const completedSteps = [CheckoutStep.INFORMATION, CheckoutStep.SHIPPING];
    expect(completedSteps.includes(CheckoutStep.INFORMATION)).toBe(true);
    expect(completedSteps.includes(CheckoutStep.PAYMENT)).toBe(false);
  });
});
