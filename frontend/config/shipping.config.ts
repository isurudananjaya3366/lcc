/**
 * Shipping Configuration
 *
 * Shipping zones, methods, rates, and delivery timeframes for Sri Lanka.
 */

export interface ShippingZone {
  id: number;
  name: string;
  areas: string[];
  deliveryDays: { min: number; max: number };
}

export interface ShippingMethod {
  id: string;
  name: string;
  description: string;
  baseRate: number;
  freeShippingThreshold: number | null;
  codSurcharge: number;
}

export const shippingZones: ShippingZone[] = [
  {
    id: 1,
    name: 'Colombo Metro',
    areas: ['Colombo 1-15', 'Dehiwala', 'Mount Lavinia', 'Kotte'],
    deliveryDays: { min: 1, max: 3 },
  },
  {
    id: 2,
    name: 'Western Province',
    areas: ['Gampaha', 'Kalutara', 'Negombo', 'Panadura'],
    deliveryDays: { min: 2, max: 4 },
  },
  {
    id: 3,
    name: 'Major Cities',
    areas: ['Kandy', 'Galle', 'Matara', 'Kurunegala', 'Anuradhapura', 'Jaffna'],
    deliveryDays: { min: 3, max: 5 },
  },
  {
    id: 4,
    name: 'Outstation',
    areas: ['Badulla', 'Ratnapura', 'Trincomalee', 'Batticaloa', 'Nuwara Eliya'],
    deliveryDays: { min: 4, max: 7 },
  },
  {
    id: 5,
    name: 'Remote Areas',
    areas: ['Kilinochchi', 'Mullaitivu', 'Mannar', 'Vavuniya'],
    deliveryDays: { min: 7, max: 10 },
  },
];

export const shippingMethods: ShippingMethod[] = [
  {
    id: 'standard',
    name: 'Standard Delivery',
    description: 'Regular delivery via local courier',
    baseRate: 350,
    freeShippingThreshold: 5000,
    codSurcharge: 100,
  },
  {
    id: 'express',
    name: 'Express Delivery',
    description: 'Next-day delivery (Colombo Metro only)',
    baseRate: 550,
    freeShippingThreshold: 10000,
    codSurcharge: 100,
  },
  {
    id: 'pickup',
    name: 'Store Pickup',
    description: 'Pick up from our Colombo store',
    baseRate: 0,
    freeShippingThreshold: null,
    codSurcharge: 0,
  },
];

/** Base rates per zone (LKR) */
export const zoneRates: Record<number, number> = {
  1: 250,
  2: 350,
  3: 450,
  4: 550,
  5: 750,
};

export const shippingConfig = {
  zones: shippingZones,
  methods: shippingMethods,
  zoneRates,
  freeShippingDefault: 5000,
  codMaxAmount: 50000,
  codSurcharge: 100,
  couriers: ['Pronto Courier', 'DHL Sri Lanka', 'Sri Lanka Post'],
} as const;
