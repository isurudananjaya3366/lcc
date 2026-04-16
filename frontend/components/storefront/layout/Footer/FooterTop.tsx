import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import FooterContainer from './FooterContainer';
import FooterLogo from './FooterLogo';
import FooterLinks from './FooterLinks';
import FooterNewsletter from './FooterNewsletter';
import FooterSocial from './FooterSocial';

interface FooterTopProps {
  className?: string;
}

const FooterTop: FC<FooterTopProps> = ({ className }) => {
  return (
    <div className={cn('pt-12 pb-8', className)}>
      <FooterContainer>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
          {/* Logo & description */}
          <div className="lg:col-span-3">
            <FooterLogo />
          </div>

          {/* Link columns */}
          <div className="lg:col-span-5">
            <FooterLinks />
          </div>

          {/* Newsletter & Social */}
          <div className="lg:col-span-4 space-y-6">
            <FooterNewsletter />
            <FooterSocial />
          </div>
        </div>
      </FooterContainer>
    </div>
  );
};

export default FooterTop;
