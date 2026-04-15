interface ItemsCountDisplayProps {
  count: number;
}

export function ItemsCountDisplay({ count }: ItemsCountDisplayProps) {
  if (count === 0) return null;

  return (
    <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500">
      <span>
        {count} {count === 1 ? 'item' : 'items'}
      </span>
    </div>
  );
}
