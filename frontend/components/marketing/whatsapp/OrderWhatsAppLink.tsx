'use client';

import { WhatsAppButton } from './WhatsAppButton';

interface OrderWhatsAppLinkProps {
  orderId: string;
  className?: string;
}

export function OrderWhatsAppLink({ orderId, className = '' }: OrderWhatsAppLinkProps) {
  return (
    <WhatsAppButton
      messageType="order_support"
      data={{ orderId }}
      label="Get help with this order"
      variant="outline"
      size="sm"
      className={className}
    />
  );
}
