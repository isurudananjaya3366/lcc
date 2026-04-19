import { PageLayout, PageHeader } from '@/components/storefront/cms/Layout';
import { ContactInfo } from './ContactInfo';
import { WhatsAppContact } from './WhatsAppContact';
import { ContactForm } from './ContactForm';

export function ContactPage() {
  return (
    <PageLayout>
      <PageHeader
        title="Contact Us"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'Contact Us' },
        ]}
      />
      <div className="grid gap-8 lg:grid-cols-[1fr_1.5fr]">
        <div className="space-y-6">
          <ContactInfo />
          <WhatsAppContact />
        </div>
        <ContactForm />
      </div>
    </PageLayout>
  );
}
