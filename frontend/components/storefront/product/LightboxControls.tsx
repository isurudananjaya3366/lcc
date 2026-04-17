'use client';

interface LightboxControlsProps {
  currentIndex: number;
  totalImages: number;
  onClose: () => void;
}

export function LightboxControls({
  currentIndex,
  totalImages,
  onClose,
}: LightboxControlsProps) {
  return (
    <div className="absolute top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-3">
      {/* Image counter */}
      <span className="text-white/80 text-sm font-medium select-none">
        {currentIndex + 1} / {totalImages}
      </span>

      {/* Close button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onClose();
        }}
        aria-label="Close lightbox"
        className="rounded-full bg-white/10 hover:bg-white/20 p-2 text-white transition-colors"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>
  );
}
