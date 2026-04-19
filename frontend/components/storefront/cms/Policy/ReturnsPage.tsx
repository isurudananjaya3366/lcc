import type { PolicySection } from '@/types/storefront/cms.types';
import { PolicyTemplate } from './PolicyTemplate';

const returnSteps = [
  { number: 1, label: 'Contact Us', description: 'Reach out via email or phone to request a return' },
  { number: 2, label: 'Get Label', description: 'Receive your return authorisation and shipping label' },
  { number: 3, label: 'Ship Item', description: 'Pack the item securely and ship it back' },
  { number: 4, label: 'Refund', description: 'Refund processed once item is received and inspected' },
];

const stepsHtml = `
<div class="grid grid-cols-2 md:grid-cols-4 gap-4 my-6">
  ${returnSteps
    .map(
      (s) =>
        `<div class="text-center">
          <div class="mx-auto w-10 h-10 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center mb-2">${s.number}</div>
          <p class="font-medium text-sm">${s.label}</p>
          <p class="text-xs text-muted-foreground mt-1">${s.description}</p>
        </div>`
    )
    .join('')}
</div>`;

const sections: PolicySection[] = [
  {
    id: 'eligibility',
    title: 'Return Eligibility',
    content:
      '<p>Items are eligible for return within 14 days of delivery. Products must be unused, in their original packaging, and accompanied by the original receipt or proof of purchase. Items must be in the same condition as received with all tags attached.</p>',
    order: 1,
  },
  {
    id: 'process',
    title: 'Return Process',
    content:
      '<p>Follow these simple steps to return an item:</p>' + stepsHtml,
    order: 2,
  },
  {
    id: 'refunds',
    title: 'Refund Policy',
    content:
      '<p>Refunds are processed within 5–7 business days after we receive and inspect the returned item. The refund will be credited to the original payment method. Shipping costs are non-refundable unless the return is due to an error on our part. Cash on delivery orders will be refunded via bank transfer.</p>',
    order: 3,
  },
  {
    id: 'exchanges',
    title: 'Exchanges',
    content:
      '<p>Exchanges are subject to product availability. If the desired replacement is in stock, we will ship it at no additional delivery charge. If the replacement has a different price, the difference will be charged or refunded accordingly.</p>',
    order: 4,
  },
  {
    id: 'non-returnable',
    title: 'Non-Returnable Items',
    content:
      '<p>The following items cannot be returned: perishable goods, personal care and hygiene products, custom or personalised items, downloadable software, gift cards, and items marked as final sale.</p>',
    order: 5,
  },
  {
    id: 'contact',
    title: 'Contact',
    content:
      '<p>For returns and exchanges, please contact us at returns@store.lk or call +94 11 234 5678. Our returns team is available Monday to Friday, 9:00 AM to 5:00 PM Sri Lanka time.</p>',
    order: 6,
  },
];

const relatedPolicies = [
  { title: 'Shipping Information', slug: 'shipping' },
  { title: 'Terms & Conditions', slug: 'terms' },
];

export function ReturnsPage() {
  return (
    <PolicyTemplate
      title="Return Policy"
      sections={sections}
      updatedAt="January 1, 2026"
      relatedPolicies={relatedPolicies}
    />
  );
}
