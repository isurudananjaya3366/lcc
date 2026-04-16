import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import FooterLinkColumn from './FooterLinkColumn';

const linkColumns = [
  {
    title: 'Shop',
    links: [
      { label: 'Products', href: '/products' },
      { label: 'Categories', href: '/categories' },
      { label: 'Sale', href: '/sale' },
      { label: 'New Arrivals', href: '/new-arrivals' },
    ],
  },
  {
    title: 'Account',
    links: [
      { label: 'Login', href: '/login' },
      { label: 'Register', href: '/register' },
      { label: 'My Orders', href: '/account/orders' },
      { label: 'Wishlist', href: '/account/wishlist' },
    ],
  },
  {
    title: 'Support',
    links: [
      { label: 'Contact Us', href: '/contact' },
      { label: 'FAQ', href: '/faq' },
      { label: 'Returns', href: '/returns' },
      { label: 'Shipping Info', href: '/shipping' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Terms of Service', href: '/terms' },
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Cookie Policy', href: '/cookies' },
      { label: 'Refund Policy', href: '/refunds' },
    ],
  },
];

interface FooterLinksProps {
  className?: string;
}

const FooterLinks: FC<FooterLinksProps> = ({ className }) => {
  return (
    <div className={cn('grid grid-cols-2 md:grid-cols-4 gap-8', className)}>
      {linkColumns.map((column) => (
        <FooterLinkColumn key={column.title} title={column.title} links={column.links} />
      ))}
    </div>
  );
};

export default FooterLinks;
