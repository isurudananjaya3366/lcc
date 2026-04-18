'use client';

interface OrdersHeaderProps {
  total: number;
}

export function OrdersHeader({ total }: OrdersHeaderProps) {
  return (
    <div className="flex flex-col gap-1">
      <h2 className="text-2xl font-bold tracking-tight">My Orders</h2>
      <p className="text-sm text-muted-foreground">
        {total === 0
          ? 'No orders yet'
          : `${total} order${total !== 1 ? 's' : ''} found`}
      </p>
    </div>
  );
}
