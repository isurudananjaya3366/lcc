import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import FooterTop from './FooterTop';
import FooterBottom from './FooterBottom';

interface FooterProps {
  className?: string;
}

const Footer: FC<FooterProps> = ({ className }) => {
  return (
    <footer className={cn('bg-gray-900 text-gray-300', className)} role="contentinfo">
      <FooterTop />
      <FooterBottom />
    </footer>
  );
};

export default Footer;
