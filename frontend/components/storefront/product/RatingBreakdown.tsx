interface RatingBreakdownProps {
  distribution: Record<number, number>;
  totalReviews: number;
}

export function RatingBreakdown({ distribution, totalReviews }: RatingBreakdownProps) {
  const stars = [5, 4, 3, 2, 1];

  return (
    <div className="space-y-2">
      {stars.map((star) => {
        const count = distribution[star] ?? 0;
        const percentage = totalReviews > 0 ? (count / totalReviews) * 100 : 0;

        return (
          <div key={star} className="flex items-center gap-3 text-sm">
            <span className="w-8 text-right text-gray-600">{star} ★</span>
            <div className="flex-1 h-2.5 rounded-full bg-gray-200 overflow-hidden">
              <div
                className="h-full rounded-full bg-yellow-400 transition-all duration-300"
                style={{ width: `${percentage}%` }}
              />
            </div>
            <span className="w-8 text-gray-500">{count}</span>
          </div>
        );
      })}
    </div>
  );
}
