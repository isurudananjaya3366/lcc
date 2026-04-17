'use client';

interface ImageErrorStateProps {
  productName: string;
  className?: string;
}

export function ImageErrorState({ productName, className = '' }: ImageErrorStateProps) {
  return (
    <div
      className={`bg-gray-100 flex flex-col items-center justify-center gap-2 ${className}`}
      role="img"
      aria-label={`Image unavailable for ${productName}`}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-gray-400"
      >
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
        <line x1="2" y1="2" x2="22" y2="22" />
      </svg>
      <span className="text-gray-400 text-xs text-center px-4 truncate max-w-full">
        {productName}
      </span>
    </div>
  );
}
