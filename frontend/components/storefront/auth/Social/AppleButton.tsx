'use client';

import { Button } from '@/components/ui/button';

export interface AppleButtonProps {
  disabled?: boolean;
  onClick?: () => void;
}

export function AppleButton({ disabled = false, onClick }: AppleButtonProps) {
  return (
    <Button
      variant="outline"
      type="button"
      disabled={disabled}
      onClick={onClick}
      aria-label="Continue with Apple"
      className="w-full gap-2"
    >
      {/* Apple icon (SVG) */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 814 1000"
        className="h-4 w-4 shrink-0"
        aria-hidden="true"
        fill="currentColor"
      >
        <path d="M788.1 340.9c-5.8 4.5-108.2 62.2-108.2 190.5 0 148.4 130.3 200.9 134.2 202.2-.6 3.2-20.7 71.9-68.7 141.9-42.8 61.6-87.5 123.1-155.5 123.1s-85.5-39.5-164-39.5c-76 0-103.7 40.8-165.9 40.8s-105-37.5-155.5-105.5c-59.3-81.8-107.2-213.3-107.2-344.3 0-200.4 132.3-306.8 260.4-306.8 67.1 0 122.8 44.6 164.6 44.6 39.8 0 102.4-47.1 178.5-47.1 28.3 0 130.5 2.6 198.5 99.2zm-234-181.5c31.1-36.9 53.1-88.1 53.1-139.3 0-7.1-.6-14.3-1.9-20.1-50.6 1.9-110.8 33.7-147.1 75.8-28.5 32.4-55.1 83.6-55.1 135.5 0 7.8 1.3 15.6 1.9 18.1 3.2.6 8.4 1.3 13.6 1.3 45.4 0 102.5-30.4 135.5-71.3z" />
      </svg>
      Apple
    </Button>
  );
}
