'use client';

import { cn } from '@/lib/utils';

interface CardQuickActionsProps {
  productId: string;
  onQuickView?: () => void;
  className?: string;
}

function ActionButton({
  label,
  onClick,
  children,
}: {
  label: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={(e) => {
        e.stopPropagation();
        e.preventDefault();
        onClick();
      }}
      className="w-8 h-8 rounded-full bg-white/90 shadow-sm flex items-center justify-center hover:bg-blue-50 transition-colors"
    >
      {children}
    </button>
  );
}

export function CardQuickActions({ productId, onQuickView, className }: CardQuickActionsProps) {
  return (
    <div
      className={cn(
        'absolute top-2 right-2 z-30 flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200',
        className
      )}
    >
      {/* Wishlist */}
      <ActionButton label="Add to wishlist" onClick={() => {}}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>
      </ActionButton>

      {/* Quick View */}
      <ActionButton
        label="Quick view"
        onClick={() => {
          onQuickView?.();
        }}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      </ActionButton>

      {/* Compare */}
      <ActionButton label="Compare" onClick={() => {}}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polygon points="12 2 2 7 12 12 22 7 12 2" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
      </ActionButton>
    </div>
  );
}
