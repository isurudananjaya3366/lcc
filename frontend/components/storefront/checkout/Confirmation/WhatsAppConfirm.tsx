'use client';

import { Phone } from 'lucide-react';

interface WhatsAppConfirmProps {
  phone: string;
}

export const WhatsAppConfirm = ({ phone }: WhatsAppConfirmProps) => {
  const masked = phone ? `+94 ${phone.slice(0, 3)} ${phone.slice(3, 6)} ${phone.slice(6)}` : '';

  return (
    <div className="flex items-start gap-3 rounded-lg bg-emerald-50 p-4 border border-emerald-200">
      <Phone className="h-5 w-5 shrink-0 text-emerald-600 mt-0.5" />
      <p className="text-sm text-emerald-800">
        Order updates will be sent to <span className="font-medium">{masked}</span> via WhatsApp.
      </p>
    </div>
  );
};
