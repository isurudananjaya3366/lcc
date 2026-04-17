interface StarRatingProps {
  rating: number;
  maxStars?: number;
  size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
};

export function StarRating({ rating, maxStars = 5, size = 'md' }: StarRatingProps) {
  const stars = Array.from({ length: maxStars }, (_, i) => {
    const fill = Math.min(1, Math.max(0, rating - i));
    return { index: i, fill };
  });

  return (
    <div className="flex items-center gap-0.5" aria-label={`${rating} out of ${maxStars} stars`}>
      {stars.map(({ index, fill }) => (
        <svg
          key={index}
          className={`${sizeClasses[size]} ${fill >= 1 ? 'text-yellow-400' : fill > 0 ? 'text-yellow-400' : 'text-gray-300'}`}
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          {fill > 0 && fill < 1 ? (
            <>
              <defs>
                <linearGradient id={`star-grad-${index}`}>
                  <stop offset={`${fill * 100}%`} stopColor="currentColor" />
                  <stop offset={`${fill * 100}%`} stopColor="#D1D5DB" />
                </linearGradient>
              </defs>
              <path
                fill={`url(#star-grad-${index})`}
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </>
          ) : (
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          )}
        </svg>
      ))}
    </div>
  );
}
