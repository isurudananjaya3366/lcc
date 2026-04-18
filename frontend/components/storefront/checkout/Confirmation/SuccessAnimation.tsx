'use client';

export const SuccessAnimation = () => {
  return (
    <div className="flex items-center justify-center">
      <div className="relative flex h-24 w-24 items-center justify-center rounded-full bg-green-100 animate-[scaleIn_0.5s_ease-out]">
        <svg
          className="h-12 w-12 text-green-600 animate-[fadeIn_0.6s_ease-out_0.3s_both]"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={3}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 13l4 4L19 7"
            className="animate-[drawCheck_0.4s_ease-out_0.5s_both]"
            style={{
              strokeDasharray: 24,
              strokeDashoffset: 24,
            }}
          />
        </svg>
      </div>

      {/* Inline keyframes */}
      <style jsx>{`
        @keyframes scaleIn {
          0% {
            transform: scale(0);
            opacity: 0;
          }
          60% {
            transform: scale(1.1);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes drawCheck {
          to {
            stroke-dashoffset: 0;
          }
        }
      `}</style>
    </div>
  );
};
