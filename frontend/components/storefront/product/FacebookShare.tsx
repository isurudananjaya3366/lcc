'use client';

interface FacebookShareProps {
  productUrl: string;
}

export function FacebookShare({ productUrl }: FacebookShareProps) {
  const handleShare = () => {
    const url = encodeURIComponent(productUrl);
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${url}`,
      '_blank',
      'noopener,noreferrer,width=600,height=400'
    );
  };

  return (
    <button
      onClick={handleShare}
      className="inline-flex items-center justify-center rounded-full p-2 text-blue-600 hover:bg-blue-50 transition-colors"
      aria-label="Share on Facebook"
      title="Share on Facebook"
    >
      <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
      </svg>
    </button>
  );
}
