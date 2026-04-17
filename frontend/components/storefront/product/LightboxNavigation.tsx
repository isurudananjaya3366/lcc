'use client';

interface LightboxNavigationProps {
  onPrev: () => void;
  onNext: () => void;
  hasPrev: boolean;
  hasNext: boolean;
}

export function LightboxNavigation({
  onPrev,
  onNext,
  hasPrev,
  hasNext,
}: LightboxNavigationProps) {
  return (
    <>
      {/* Previous button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onPrev();
        }}
        disabled={!hasPrev}
        aria-label="Previous image"
        className="absolute left-4 top-1/2 -translate-y-1/2 z-50 rounded-full bg-white/10 hover:bg-white/20 p-3 text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>

      {/* Next button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onNext();
        }}
        disabled={!hasNext}
        aria-label="Next image"
        className="absolute right-4 top-1/2 -translate-y-1/2 z-50 rounded-full bg-white/10 hover:bg-white/20 p-3 text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
    </>
  );
}
