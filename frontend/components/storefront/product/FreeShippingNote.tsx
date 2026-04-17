export function FreeShippingNote() {
  return (
    <div className="flex items-center gap-1.5 text-sm text-green-700">
      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      </svg>
      <span className="font-medium">Free Shipping</span>
    </div>
  );
}
