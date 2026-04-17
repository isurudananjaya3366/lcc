'use client';

interface ImageLoadingStateProps {
  className?: string;
}

export function ImageLoadingState({ className = '' }: ImageLoadingStateProps) {
  return (
    <div
      className={`bg-gray-200 animate-pulse flex items-center justify-center ${className}`}
      aria-label="Loading image"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-gray-300"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
    </div>
  );
}
