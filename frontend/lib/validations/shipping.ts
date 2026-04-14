import { z } from 'zod';

export const carriers = [
  { value: 'DHL', label: 'DHL', trackingPattern: /^DHL\d{10}$/i, hint: 'DHL + 10 digits' },
  { value: 'FEDEX', label: 'FedEx', trackingPattern: /^FDX\d{12}$/i, hint: 'FDX + 12 digits' },
  { value: 'UPS', label: 'UPS', trackingPattern: /^1Z[A-Z0-9]{16}$/i, hint: '1Z + 16 chars' },
  {
    value: 'SL_POST',
    label: 'Sri Lanka Post',
    trackingPattern: /^[A-Z]{2}\d{9}[A-Z]{2}$/i,
    hint: '2 letters + 9 digits + 2 letters',
  },
  { value: 'PRONTO', label: 'Pronto', trackingPattern: /^PRN\d{8}$/i, hint: 'PRN + 8 digits' },
  { value: 'CUSTOM', label: 'Custom / Other', trackingPattern: null, hint: 'Any format' },
] as const;

export const serviceLevels = [
  { value: 'STANDARD', label: 'Standard' },
  { value: 'EXPRESS', label: 'Express' },
  { value: 'OVERNIGHT', label: 'Overnight' },
  { value: 'ECONOMY', label: 'Economy' },
] as const;

export type CarrierValue = (typeof carriers)[number]['value'];
export type ServiceLevelValue = (typeof serviceLevels)[number]['value'];

export const shippingFormSchema = z.object({
  carrier: z.string().min(1, 'Carrier is required'),
  serviceLevel: z.string().min(1, 'Service level is required'),
  trackingNumber: z.string().optional(),
  shippingNotes: z.string().max(500, 'Max 500 characters').optional(),
  notifyCustomer: z.boolean().default(true),
});

export type ShippingFormValues = z.infer<typeof shippingFormSchema>;
