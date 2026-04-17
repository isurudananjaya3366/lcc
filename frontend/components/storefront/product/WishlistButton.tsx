'use client';

import { useWishlistStore } from '@/stores/store/wishlist';

interface WishlistButtonProps {
  productId: string;
  productName: string;
  productSlug: string;
  price: number;
  salePrice: number | null;
  image: string;
  inStock: boolean;
}

export function WishlistButton({
  productId,
  productName,
  productSlug,
  price,
  salePrice,
  image,
  inStock,
}: WishlistButtonProps) {
  const isInWishlist = useWishlistStore((s) => s.isInWishlist(productId));
  const toggle = useWishlistStore((s) => s.toggle);

  const handleToggle = () => {
    toggle({
      productId,
      name: productName,
      slug: productSlug,
      price,
      salePrice,
      image,
      inStock,
      addedAt: new Date().toISOString(),
    });
  };

  return (
    <button
      onClick={handleToggle}
      className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-red-600 transition-colors"
      aria-label={isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
    >
      {isInWishlist ? (
        <svg className="h-5 w-5 text-red-500" viewBox="0 0 24 24" fill="currentColor">
          <path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z" />
        </svg>
      ) : (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
        </svg>
      )}
      {isInWishlist ? 'In Wishlist' : 'Add to Wishlist'}
    </button>
  );
}
