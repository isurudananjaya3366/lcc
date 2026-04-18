'use client';

import { SocialDivider } from './SocialDivider';
import { GoogleButton } from './GoogleButton';
import { FacebookButton } from './FacebookButton';

export interface SocialLoginButtonsProps {
  variant?: 'login' | 'register';
}

export function SocialLoginButtons({ variant = 'login' }: SocialLoginButtonsProps) {
  return (
    <div className="space-y-4">
      <SocialDivider />
      <div className="grid grid-cols-2 gap-3">
        <GoogleButton disabled />
        <FacebookButton disabled />
      </div>
      <p className="text-center text-xs text-muted-foreground">
        Social {variant === 'login' ? 'sign-in' : 'sign-up'} coming soon
      </p>
    </div>
  );
}
