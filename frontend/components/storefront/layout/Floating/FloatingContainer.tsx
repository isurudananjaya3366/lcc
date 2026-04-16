'use client';

import { cn } from '@/lib/utils';
import { ScrollToTop } from './ScrollToTop';
import { WhatsAppButton } from './WhatsAppButton';

export interface FloatingContainerProps {
  whatsappNumber: string;
  whatsappMessage?: string;
  scrollThreshold?: number;
  className?: string;
}

export function FloatingContainer({
  whatsappNumber,
  whatsappMessage,
  scrollThreshold = 400,
  className,
}: FloatingContainerProps) {
  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 md:bottom-5 md:right-5',
        'z-40 flex flex-col items-end gap-2.5 md:gap-3',
        'print:hidden',
        className
      )}
      aria-label="Floating actions"
    >
      <ScrollToTop showAfter={scrollThreshold} />
      <WhatsAppButton phoneNumber={whatsappNumber} message={whatsappMessage} />
    </div>
  );
}

export default FloatingContainer;
