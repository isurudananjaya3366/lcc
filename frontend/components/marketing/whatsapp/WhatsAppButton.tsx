'use client';

import { WhatsAppIcon } from './WhatsAppIcon';
import { getWhatsAppUrl } from '@/lib/marketing/whatsapp';
import type { WhatsAppMessageType } from '@/types/marketing/whatsapp.types';

interface WhatsAppButtonProps {
  messageType?: WhatsAppMessageType;
  data?: Record<string, unknown>;
  label?: string;
  variant?: 'primary' | 'outline' | 'icon';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-xs gap-1.5',
  md: 'px-4 py-2 text-sm gap-2',
  lg: 'px-6 py-3 text-base gap-2',
};

const variantClasses = {
  primary: 'bg-[#25D366] text-white hover:bg-[#20BD5A] shadow-sm',
  outline: 'border border-[#25D366] text-[#25D366] hover:bg-[#25D366]/5',
  icon: 'p-2 text-[#25D366] hover:bg-[#25D366]/10 rounded-full',
};

export function WhatsAppButton({
  messageType = 'general',
  data,
  label = 'Chat on WhatsApp',
  variant = 'primary',
  size = 'md',
  className = '',
}: WhatsAppButtonProps) {
  const url = getWhatsAppUrl(messageType, data);
  const iconSize = size === 'sm' ? 14 : size === 'lg' ? 20 : 16;

  if (variant === 'icon') {
    return (
      <a
        href={url}
        target="_blank"
        rel="noopener noreferrer"
        className={`inline-flex items-center justify-center rounded-full ${variantClasses.icon} ${className}`}
        aria-label="Chat on WhatsApp"
      >
        <WhatsAppIcon size={iconSize + 4} />
      </a>
    );
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className={`inline-flex items-center justify-center rounded-lg font-medium transition-colors ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      <WhatsAppIcon size={iconSize} />
      {label}
    </a>
  );
}
