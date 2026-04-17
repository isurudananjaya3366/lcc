'use client';

export function OutOfStockOverlay() {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/60 backdrop-blur-[1px] rounded-lg">
      <span className="rounded-md bg-gray-900 px-4 py-2 text-sm font-semibold uppercase tracking-wider text-white shadow-lg">
        Out of Stock
      </span>
    </div>
  );
}
