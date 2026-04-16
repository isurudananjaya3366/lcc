import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import FooterContainer from './FooterContainer';
import Copyright from './Copyright';
import PaymentIcons from './PaymentIcons';

interface FooterBottomProps {
  className?: string;
}

const FooterBottom: FC<FooterBottomProps> = ({ className }) => {
  return (
    <div className={cn('bg-gray-800 border-t border-gray-700 py-4 md:py-6', className)}>
      <FooterContainer>
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <Copyright showLinks />
          <PaymentIcons />
        </div>
      </FooterContainer>
    </div>
  );
};

export default FooterBottom;
