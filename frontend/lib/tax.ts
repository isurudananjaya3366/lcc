export interface TaxCategory {
  id: string;
  name: string;
  rate: number | null;
  description: string;
}

export const TAX_CATEGORIES: TaxCategory[] = [
  {
    id: 'standard',
    name: 'Standard',
    rate: 12,
    description: 'Most goods and services',
  },
  {
    id: 'reduced',
    name: 'Reduced',
    rate: 5,
    description: 'Essential goods (food, medicine, etc.)',
  },
  {
    id: 'zero-rated',
    name: 'Zero-rated',
    rate: 0,
    description: 'Exports and specific items',
  },
  {
    id: 'exempt',
    name: 'Exempt',
    rate: null,
    description: 'No VAT applied (financial services, etc.)',
  },
];
