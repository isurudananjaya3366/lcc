import type { PolicySection } from '@/types/storefront/cms.types';
import { PolicyTemplate } from './PolicyTemplate';

const sections: PolicySection[] = [
  {
    id: 'acceptance',
    title: 'Acceptance of Terms',
    content:
      '<p>By accessing and using this website, you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by these terms, please do not use this service.</p>',
    order: 1,
  },
  {
    id: 'use-license',
    title: 'Use License',
    content:
      '<p>Permission is granted to temporarily download one copy of the materials on our website for personal, non-commercial transitory viewing only. This is the grant of a licence, not a transfer of title. You may not modify or copy the materials, use them for any commercial purpose, or attempt to reverse engineer any software contained on the website.</p>',
    order: 2,
  },
  {
    id: 'account',
    title: 'Account Responsibilities',
    content:
      '<p>You are responsible for maintaining the confidentiality of your account and password, and for restricting access to your computer. You agree to accept responsibility for all activities that occur under your account or password. You must notify us immediately of any unauthorised use.</p>',
    order: 3,
  },
  {
    id: 'payments',
    title: 'Payment Terms',
    content:
      '<p>All prices are listed in Sri Lankan Rupees (LKR). We accept Visa, Mastercard, bank transfers, and cash on delivery. Payment must be received in full before order dispatch unless cash on delivery is selected. Prices are subject to change without notice.</p>',
    order: 4,
  },
  {
    id: 'shipping',
    title: 'Shipping & Delivery',
    content:
      '<p>We deliver across Sri Lanka. Delivery times vary by location. Standard delivery within Colombo takes 1–2 business days. Other provinces may take 3–5 business days. We are not responsible for delays caused by courier services or events beyond our control.</p>',
    order: 5,
  },
  {
    id: 'returns',
    title: 'Returns & Refunds',
    content:
      '<p>Items may be returned within 14 days of delivery provided they are unused, in original packaging, and accompanied by proof of purchase. Refunds are processed within 5–7 business days to the original payment method. Shipping costs are non-refundable unless the return is due to our error.</p>',
    order: 6,
  },
  {
    id: 'liability',
    title: 'Limitation of Liability',
    content:
      '<p>We shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising out of your access to or use of this website or any products purchased through it. Our total liability shall not exceed the amount paid for the specific product giving rise to the claim.</p>',
    order: 7,
  },
  {
    id: 'governing-law',
    title: 'Governing Law',
    content:
      '<p>These terms and conditions are governed by and construed in accordance with the laws of the Democratic Socialist Republic of Sri Lanka. Any disputes arising from these terms shall be subject to the exclusive jurisdiction of the courts of Sri Lanka.</p>',
    order: 8,
  },
];

const relatedPolicies = [
  { title: 'Privacy Policy', slug: 'privacy' },
  { title: 'Return Policy', slug: 'returns' },
];

export function TermsPage() {
  return (
    <PolicyTemplate
      title="Terms & Conditions"
      sections={sections}
      updatedAt="January 1, 2026"
      relatedPolicies={relatedPolicies}
    />
  );
}
