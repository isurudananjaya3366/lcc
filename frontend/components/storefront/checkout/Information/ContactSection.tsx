'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EmailInput } from './EmailInput';
import { PhoneInput } from './PhoneInput';
import { WhatsAppCheckbox } from './WhatsAppCheckbox';
import { LoginPrompt } from './LoginPrompt';

export const ContactSection = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Contact Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <EmailInput />
        <PhoneInput />
        <WhatsAppCheckbox />
        <LoginPrompt />
      </CardContent>
    </Card>
  );
};
