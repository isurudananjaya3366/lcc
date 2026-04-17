'use client';

interface BuyNowButtonProps {
  onBuyNow: () => void;
  disabled?: boolean;
}

export function BuyNowButton({ onBuyNow, disabled }: BuyNowButtonProps) {
  return (
    <button
      onClick={onBuyNow}
      disabled={disabled}
      className={`
        flex w-full items-center justify-center gap-2 rounded-lg border-2 px-6 py-3 text-base font-semibold transition-all
        ${disabled
          ? 'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400'
          : 'border-blue-600 bg-white text-blue-600 hover:bg-blue-50 active:scale-[0.98]'
        }
      `}
    >
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
      Buy Now
    </button>
  );
}
