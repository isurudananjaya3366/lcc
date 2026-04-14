'use client';

import { useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/cn';

export interface OTPInputProps {
  value: string;
  onChange: (value: string) => void;
  onComplete?: (value: string) => void;
  disabled?: boolean;
  hasError?: boolean;
  className?: string;
}

const OTP_LENGTH = 6;

export function OTPInput({
  value,
  onChange,
  onComplete,
  disabled = false,
  hasError = false,
  className,
}: OTPInputProps) {
  const inputsRef = useRef<(HTMLInputElement | null)[]>([]);

  const digits = value.split('').concat(Array(OTP_LENGTH).fill('')).slice(0, OTP_LENGTH);

  const focusInput = useCallback((index: number) => {
    inputsRef.current[index]?.focus();
  }, []);

  useEffect(() => {
    if (!disabled) {
      const firstEmpty = digits.findIndex((d) => !d);
      focusInput(firstEmpty >= 0 ? firstEmpty : OTP_LENGTH - 1);
    }
    // Only focus on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateValue = useCallback(
    (newDigits: string[]) => {
      const newValue = newDigits.join('');
      onChange(newValue);
      if (newValue.length === OTP_LENGTH && onComplete) {
        onComplete(newValue);
      }
    },
    [onChange, onComplete]
  );

  const handleChange = (index: number, inputValue: string) => {
    const digit = inputValue.replace(/\D/g, '').slice(-1);
    if (!digit && inputValue) return;

    const newDigits = [...digits];
    newDigits[index] = digit;
    updateValue(newDigits);

    if (digit && index < OTP_LENGTH - 1) {
      focusInput(index + 1);
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      e.preventDefault();
      const newDigits = [...digits];
      if (digits[index]) {
        newDigits[index] = '';
        updateValue(newDigits);
      } else if (index > 0) {
        newDigits[index - 1] = '';
        updateValue(newDigits);
        focusInput(index - 1);
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      e.preventDefault();
      focusInput(index - 1);
    } else if (e.key === 'ArrowRight' && index < OTP_LENGTH - 1) {
      e.preventDefault();
      focusInput(index + 1);
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!pastedData) return;

    const newDigits = pastedData.split('').concat(Array(OTP_LENGTH).fill('')).slice(0, OTP_LENGTH);
    updateValue(newDigits);

    const focusIdx = Math.min(pastedData.length, OTP_LENGTH - 1);
    focusInput(focusIdx);
  };

  return (
    <div className={cn('flex items-center justify-center gap-2 sm:gap-3', className)}>
      {digits.map((digit, index) => (
        <input
          key={index}
          ref={(el) => {
            inputsRef.current[index] = el;
          }}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={1}
          autoComplete="off"
          aria-label={`Digit ${index + 1} of ${OTP_LENGTH}`}
          disabled={disabled}
          value={digit}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={index === 0 ? handlePaste : undefined}
          onFocus={(e) => e.target.select()}
          className={cn(
            'h-12 w-10 sm:h-14 sm:w-12 rounded-lg border-2 text-center text-xl font-semibold',
            'transition-colors duration-150 outline-none',
            'focus:border-blue-500 focus:ring-2 focus:ring-blue-200',
            hasError && 'border-red-400 focus:border-red-500 focus:ring-red-200',
            !hasError && 'border-gray-300',
            disabled && 'cursor-not-allowed bg-gray-100 text-gray-400'
          )}
        />
      ))}
    </div>
  );
}
