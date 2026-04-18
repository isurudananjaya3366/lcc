'use client';

import { MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ContactSupportProps {
  orderNumber: string;
}

export function ContactSupport({ orderNumber }: ContactSupportProps) {
  const supportPhone =
    process.env.NEXT_PUBLIC_SUPPORT_PHONE ?? '94700000000';
  const message = encodeURIComponent(
    `Hi, I need help with order #${orderNumber}`
  );
  const whatsappUrl = `https://wa.me/${supportPhone}?text=${message}`;

  return (
    <Button variant="outline" asChild className="gap-2">
      <a href={whatsappUrl} target="_blank" rel="noopener noreferrer">
        <MessageCircle className="h-4 w-4" />
        Contact Support
      </a>
    </Button>
  );
}
