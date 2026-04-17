export function ProductCardSkeleton() {
  return (
    <div className="border rounded-lg bg-white overflow-hidden">
      {/* Image */}
      <div className="aspect-square bg-gray-200 animate-pulse" />

      {/* Content */}
      <div className="p-3 space-y-2">
        {/* Category */}
        <div className="h-3 w-[30%] bg-gray-200 animate-pulse rounded" />
        {/* Title line 1 */}
        <div className="h-4 w-[90%] bg-gray-200 animate-pulse rounded" />
        {/* Title line 2 */}
        <div className="h-4 w-[60%] bg-gray-200 animate-pulse rounded" />
        {/* Rating */}
        <div className="h-3 w-[40%] bg-gray-200 animate-pulse rounded" />
        {/* Price */}
        <div className="h-4 w-[35%] bg-gray-200 animate-pulse rounded" />
      </div>

      {/* Button */}
      <div className="mx-3 mb-3 h-9 bg-gray-200 animate-pulse rounded-md" />
    </div>
  );
}
