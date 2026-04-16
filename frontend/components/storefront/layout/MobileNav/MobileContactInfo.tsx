import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface MobileContactInfoProps {
  phone?: string;
  whatsapp?: string;
  hours?: string;
  showTitle?: boolean;
  className?: string;
}

const MobileContactInfo: FC<MobileContactInfoProps> = ({
  phone = '+94 77 123 4567',
  whatsapp = '94771234567',
  hours = 'Mon-Sat: 9:00 AM - 8:00 PM',
  showTitle = true,
  className,
}) => {
  const phoneHref = `tel:${phone.replace(/\s/g, '')}`;
  const whatsappHref = `https://wa.me/${whatsapp}`;

  return (
    <div
      className={cn('border-t border-gray-200 dark:border-gray-700 py-4 px-4 space-y-3', className)}
    >
      {showTitle && (
        <h3 className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-medium">
          Contact Us
        </h3>
      )}

      {/* Phone */}
      <a
        href={phoneHref}
        className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400 hover:text-green-700 dark:hover:text-green-400 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 text-gray-400 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
          />
        </svg>
        {phone}
      </a>

      {/* WhatsApp */}
      <a
        href={whatsappHref}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400 hover:text-green-700 dark:hover:text-green-400 transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 text-gray-400 flex-shrink-0"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        WhatsApp
      </a>

      {/* Hours */}
      {hours && (
        <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 text-gray-400 flex-shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          {hours}
        </div>
      )}
    </div>
  );
};

export default MobileContactInfo;
