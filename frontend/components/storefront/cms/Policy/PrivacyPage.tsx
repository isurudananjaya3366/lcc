import type { PolicySection } from '@/types/storefront/cms.types';
import { PolicyTemplate } from './PolicyTemplate';

const sections: PolicySection[] = [
  {
    id: 'info-collect',
    title: 'Information We Collect',
    content:
      '<p>We collect personal information that you provide directly, including your name, email address, phone number, delivery address, and payment details when you place an order or create an account. We also automatically collect browsing data such as IP address, browser type, and pages visited.</p>',
    order: 1,
  },
  {
    id: 'how-we-use',
    title: 'How We Use Information',
    content:
      '<p>Your information is used for order processing, customer service communications, marketing communications (with your consent), improving our website experience, fraud prevention, and complying with legal obligations.</p>',
    order: 2,
  },
  {
    id: 'data-protection',
    title: 'Data Protection',
    content:
      '<p>We implement SSL encryption across our entire website, use secure payment processing through PCI-DSS certified gateways, and store your data on protected servers with restricted access controls. Regular security audits are performed to ensure data integrity.</p>',
    order: 3,
  },
  {
    id: 'cookies',
    title: 'Cookies',
    content:
      '<p>We use cookies to maintain your session, remember your preferences, analyse site traffic, and personalise your shopping experience. Essential cookies are required for the website to function. You can manage non-essential cookie settings through your browser preferences.</p>',
    order: 4,
  },
  {
    id: 'third-parties',
    title: 'Third-Party Services',
    content:
      '<p>We share necessary data with trusted third parties including payment processors, delivery partners, and analytics providers. These parties are bound by confidentiality agreements and data protection regulations. We do not sell your personal information to third parties.</p>',
    order: 5,
  },
  {
    id: 'your-rights',
    title: 'Your Rights',
    content:
      '<p>You have the right to access, correct, or delete your personal data at any time. You may also opt out of marketing communications, request a copy of the information we hold about you, and lodge a complaint with the relevant data protection authority.</p>',
    order: 6,
  },
  {
    id: 'contact',
    title: 'Contact Us',
    content:
      '<p>For privacy-related concerns, please contact our data protection team at privacy@store.lk or write to us at our registered office in Colombo 03, Sri Lanka. We aim to respond to all enquiries within 48 hours.</p>',
    order: 7,
  },
];

const relatedPolicies = [
  { title: 'Terms & Conditions', slug: 'terms' },
  { title: 'Return Policy', slug: 'returns' },
];

export function PrivacyPage() {
  return (
    <PolicyTemplate
      title="Privacy Policy"
      sections={sections}
      updatedAt="January 1, 2026"
      relatedPolicies={relatedPolicies}
    />
  );
}
