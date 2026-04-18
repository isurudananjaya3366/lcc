'use client';

interface WishlistHeaderProps {
  count: number;
}

export function WishlistHeader({ count }: WishlistHeaderProps) {
  return (
    <div className="flex flex-col gap-1">
      <h2 className="text-2xl font-bold tracking-tight">My Wishlist</h2>
      <p className="text-sm text-muted-foreground">
        {count === 0
          ? 'No items saved yet'
          : `${count} item${count !== 1 ? 's' : ''} saved`}
      </p>
    </div>
  );
}
