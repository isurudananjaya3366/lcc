'use client';

interface ReviewCountLinkProps {
  count: number;
  productId: number;
}

export function ReviewCountLink({ count }: ReviewCountLinkProps) {
  const handleClick = () => {
    const reviewsSection = document.getElementById('product-reviews');
    if (reviewsSection) {
      reviewsSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <button
      onClick={handleClick}
      className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
    >
      ({count} {count === 1 ? 'review' : 'reviews'})
    </button>
  );
}
