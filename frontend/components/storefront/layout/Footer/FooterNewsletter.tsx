import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import NewsletterForm from './NewsletterForm';

interface FooterNewsletterProps {
  className?: string;
}

const FooterNewsletter: FC<FooterNewsletterProps> = ({ className }) => {
  return (
    <div className={cn('', className)}>
      <h3 className="text-lg font-semibold text-white">Subscribe to Our Newsletter</h3>
      <p className="text-sm text-gray-400 mt-2 mb-4">
        Get updates on sales, new products, and exclusive offers.
      </p>
      <NewsletterForm />
    </div>
  );
};

export default FooterNewsletter;
