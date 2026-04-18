'use client';

import { Mail, Phone, User } from 'lucide-react';
import { useStoreCheckoutStore } from '@/stores/store';

export const ContactSummary = () => {
  const contactInfo = useStoreCheckoutStore((s) => s.contactInfo);

  const fullName = [contactInfo.firstName, contactInfo.lastName].filter(Boolean).join(' ');

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 text-sm">
        <User className="h-4 w-4 shrink-0 text-gray-400" />
        <span className="text-gray-900">{fullName || '—'}</span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <Mail className="h-4 w-4 shrink-0 text-gray-400" />
        <span className="text-gray-900">{contactInfo.email || '—'}</span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        <Phone className="h-4 w-4 shrink-0 text-gray-400" />
        <span className="text-gray-900">
          {contactInfo.phone ? `+94 ${contactInfo.phone}` : '—'}
        </span>
      </div>
    </div>
  );
};
