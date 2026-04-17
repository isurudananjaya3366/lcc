import { cn } from '@/lib/utils';

type IllustrationVariant = 'search' | 'filter' | 'empty';

interface EmptyStateIllustrationProps {
  variant?: IllustrationVariant;
  size?: number;
  className?: string;
}

function SearchIllustration({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" aria-hidden="true">
      <circle cx="52" cy="52" r="36" stroke="#D1D5DB" strokeWidth="4" />
      <line
        x1="78"
        y1="78"
        x2="104"
        y2="104"
        stroke="#D1D5DB"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <path d="M42 48h20M42 56h12" stroke="#9CA3AF" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

function FilterIllustration({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" aria-hidden="true">
      <path
        d="M24 30h72L66 66v24l-12 6V66L24 30z"
        stroke="#D1D5DB"
        strokeWidth="4"
        strokeLinejoin="round"
      />
      <circle cx="90" cy="30" r="12" fill="#FEE2E2" stroke="#F87171" strokeWidth="2" />
      <path d="M86 30h8M90 26v8" stroke="#F87171" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function EmptyIllustration({ size }: { size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" fill="none" aria-hidden="true">
      <rect x="20" y="30" width="80" height="60" rx="4" stroke="#D1D5DB" strokeWidth="4" />
      <path d="M20 50h80" stroke="#D1D5DB" strokeWidth="4" />
      <circle cx="60" cy="75" r="8" stroke="#9CA3AF" strokeWidth="3" />
      <path d="M56 75h8" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

export function EmptyStateIllustration({
  variant = 'empty',
  size = 120,
  className,
}: EmptyStateIllustrationProps) {
  const illustrations: Record<IllustrationVariant, React.ReactNode> = {
    search: <SearchIllustration size={size} />,
    filter: <FilterIllustration size={size} />,
    empty: <EmptyIllustration size={size} />,
  };

  return (
    <div
      className={cn('flex items-center justify-center', className)}
      role="img"
      aria-label={`${variant} empty state illustration`}
    >
      {illustrations[variant]}
    </div>
  );
}
