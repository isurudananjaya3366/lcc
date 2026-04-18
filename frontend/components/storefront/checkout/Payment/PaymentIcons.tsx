'use client';

export const PaymentIcons = () => {
  return (
    <div className="flex items-center gap-2">
      <span className="inline-flex items-center rounded border border-gray-300 bg-white px-2 py-0.5 text-[10px] font-bold text-blue-800 tracking-wider">
        VISA
      </span>
      <span className="inline-flex items-center rounded border border-gray-300 bg-white px-2 py-0.5 text-[10px] font-bold text-red-600 tracking-wider">
        MC
      </span>
      <span className="inline-flex items-center rounded border border-gray-300 bg-white px-2 py-0.5 text-[10px] font-bold text-green-700 tracking-wider">
        LankaQR
      </span>
    </div>
  );
};
