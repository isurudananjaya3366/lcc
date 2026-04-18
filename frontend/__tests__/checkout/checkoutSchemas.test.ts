/**
 * Checkout Schemas Validation Tests — Task 94 (Unit Testing Suite)
 *
 * Tests all Zod validation schemas used in the checkout flow.
 * Covers: informationStepSchema, shippingStepSchema, paymentStepSchema
 */

import { describe, it, expect } from 'vitest';
import {
  informationStepSchema,
  shippingStepSchema,
  paymentStepSchema,
} from '@/lib/validations/checkoutSchemas';

// ─── Information Step Schema ──────────────────────────────────────────────────

describe('informationStepSchema', () => {
  const validData = {
    email: 'test@example.com',
    phone: '771234567',
    firstName: 'Kasun',
    lastName: 'Perera',
    whatsappOptIn: true,
  };

  it('validates correct data', () => {
    const result = informationStepSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('rejects empty email', () => {
    const result = informationStepSchema.safeParse({ ...validData, email: '' });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('email');
    }
  });

  it('rejects invalid email format', () => {
    const result = informationStepSchema.safeParse({ ...validData, email: 'not-an-email' });
    expect(result.success).toBe(false);
  });

  it('lowercases email on valid parse', () => {
    const result = informationStepSchema.safeParse({ ...validData, email: 'TEST@EXAMPLE.COM' });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.email).toBe('test@example.com');
    }
  });

  it('rejects phone not starting with 7', () => {
    const result = informationStepSchema.safeParse({ ...validData, phone: '011234567' });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('phone');
    }
  });

  it('rejects phone shorter than 9 digits', () => {
    const result = informationStepSchema.safeParse({ ...validData, phone: '712345' });
    expect(result.success).toBe(false);
  });

  it('rejects phone longer than 9 digits', () => {
    const result = informationStepSchema.safeParse({ ...validData, phone: '7712345678' });
    expect(result.success).toBe(false);
  });

  it('accepts valid 9-digit Sri Lankan phone starting with 7', () => {
    const result = informationStepSchema.safeParse({ ...validData, phone: '712345678' });
    expect(result.success).toBe(true);
  });

  it('rejects firstName shorter than 2 chars', () => {
    const result = informationStepSchema.safeParse({ ...validData, firstName: 'K' });
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].path).toContain('firstName');
    }
  });

  it('rejects firstName longer than 50 chars', () => {
    const result = informationStepSchema.safeParse({
      ...validData,
      firstName: 'K'.repeat(51),
    });
    expect(result.success).toBe(false);
  });

  it('rejects lastName shorter than 2 chars', () => {
    const result = informationStepSchema.safeParse({ ...validData, lastName: 'P' });
    expect(result.success).toBe(false);
  });

  it('defaults whatsappOptIn to true when not provided', () => {
    const { whatsappOptIn: _w, ...rest } = validData;
    const result = informationStepSchema.safeParse(rest);
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.whatsappOptIn).toBe(true);
    }
  });

  it('accepts whatsappOptIn as false', () => {
    const result = informationStepSchema.safeParse({ ...validData, whatsappOptIn: false });
    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.whatsappOptIn).toBe(false);
    }
  });
});

// ─── Shipping Step Schema ──────────────────────────────────────────────────────

describe('shippingStepSchema', () => {
  const validData = {
    province: 'Western Province',
    district: 'Colombo',
    city: 'Colombo 03',
    address1: '123 Galle Road',
    address2: 'Apt 4B',
    landmark: 'Near Cinnamon Grand',
    postalCode: '00300',
    shippingMethodId: 'standard',
  };

  it('validates correct data', () => {
    const result = shippingStepSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it('rejects empty province', () => {
    const result = shippingStepSchema.safeParse({ ...validData, province: '' });
    expect(result.success).toBe(false);
  });

  it('rejects empty district', () => {
    const result = shippingStepSchema.safeParse({ ...validData, district: '' });
    expect(result.success).toBe(false);
  });

  it('rejects empty city', () => {
    const result = shippingStepSchema.safeParse({ ...validData, city: '' });
    expect(result.success).toBe(false);
  });

  it('rejects empty address1', () => {
    const result = shippingStepSchema.safeParse({ ...validData, address1: '' });
    expect(result.success).toBe(false);
  });

  it('rejects address1 longer than 100 chars', () => {
    const result = shippingStepSchema.safeParse({
      ...validData,
      address1: 'A'.repeat(101),
    });
    expect(result.success).toBe(false);
  });

  it('accepts optional address2', () => {
    const { address2: _a, ...rest } = validData;
    const result = shippingStepSchema.safeParse(rest);
    expect(result.success).toBe(true);
  });

  it('accepts optional landmark', () => {
    const { landmark: _l, ...rest } = validData;
    const result = shippingStepSchema.safeParse(rest);
    expect(result.success).toBe(true);
  });

  it('rejects invalid postal code (not 5 digits)', () => {
    const result = shippingStepSchema.safeParse({ ...validData, postalCode: '003' });
    expect(result.success).toBe(false);
  });

  it('rejects postal code with letters', () => {
    const result = shippingStepSchema.safeParse({ ...validData, postalCode: 'ABCDE' });
    expect(result.success).toBe(false);
  });

  it('accepts valid 5-digit postal code', () => {
    const result = shippingStepSchema.safeParse({ ...validData, postalCode: '10250' });
    expect(result.success).toBe(true);
  });

  it('rejects empty shippingMethodId', () => {
    const result = shippingStepSchema.safeParse({ ...validData, shippingMethodId: '' });
    expect(result.success).toBe(false);
  });

  it('accepts express shipping method id', () => {
    const result = shippingStepSchema.safeParse({ ...validData, shippingMethodId: 'express' });
    expect(result.success).toBe(true);
  });
});

// ─── Payment Step Schema ──────────────────────────────────────────────────────

describe('paymentStepSchema', () => {
  it('accepts payhere method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'payhere' });
    expect(result.success).toBe(true);
  });

  it('accepts card method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'card' });
    expect(result.success).toBe(true);
  });

  it('accepts bank_transfer method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'bank_transfer' });
    expect(result.success).toBe(true);
  });

  it('accepts cod method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'cod' });
    expect(result.success).toBe(true);
  });

  it('accepts koko method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'koko' });
    expect(result.success).toBe(true);
  });

  it('accepts mintpay method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'mintpay' });
    expect(result.success).toBe(true);
  });

  it('rejects unknown payment method', () => {
    const result = paymentStepSchema.safeParse({ methodType: 'bitcoin' });
    expect(result.success).toBe(false);
  });

  it('rejects empty methodType', () => {
    const result = paymentStepSchema.safeParse({ methodType: '' });
    expect(result.success).toBe(false);
  });

  it('accepts optional bankReceipt field', () => {
    const result = paymentStepSchema.safeParse({
      methodType: 'bank_transfer',
      bankReceipt: 'receipt-123',
    });
    expect(result.success).toBe(true);
  });
});
