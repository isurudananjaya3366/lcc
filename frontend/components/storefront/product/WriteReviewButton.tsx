'use client';

import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface WriteReviewButtonProps {
  productId: number;
}

export function WriteReviewButton({ productId: _productId }: WriteReviewButtonProps) {
  const router = useRouter();

  const handleClick = () => {
    // Check if user is logged in via auth token
    const hasToken =
      typeof window !== 'undefined' &&
      (localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token'));

    if (!hasToken) {
      toast.error('Please sign in to write a review', {
        action: {
          label: 'Sign In',
          onClick: () => router.push('/auth/login?next=' + window.location.pathname),
        },
      });
      return;
    }

    // Navigate to review form (scroll to review form section)
    const reviewSection = document.getElementById('write-review-form');
    if (reviewSection) {
      reviewSection.scrollIntoView({ behavior: 'smooth' });
    } else {
      toast.info('Review form coming soon!');
    }
  };

  return (
    <button
      onClick={handleClick}
      className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
    >
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
      </svg>
      Write a Review
    </button>
  );
}
